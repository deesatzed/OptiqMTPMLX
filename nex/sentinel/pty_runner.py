"""
PtyAgentRunner - adapted from gemOptq for supervising external AI agents (Claude Code, Codex/Cursor, Gemini, etc.)
under Grok-in-the-Loop + Sentinel policy.

This allows wrapping real .claude / .codex commands with full policy, enforcement, Grok escalation, and traces.
"""

from __future__ import annotations

import logging
import os
import pty
import queue
import signal
import subprocess
import threading
import termios
import fcntl
import struct

logger = logging.getLogger(__name__)


class PtyAgentRunner:
    def __init__(
        self,
        command: str,
        *,
        cwd: str | None = None,
        terminal_rows: int = 24,
        terminal_cols: int = 80,
    ):
        self.command = command
        self.cwd = cwd
        self.terminal_rows = terminal_rows
        self.terminal_cols = terminal_cols
        self.process = None
        self.output_queue = queue.Queue()
        self.reader_thread = None
        self.master_fd = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

    def start(self):
        with self._lock:
            if self.process and self.process.poll() is None:
                raise RuntimeError("Process is already active")

            master_fd, slave_fd = pty.openpty()
            try:
                self._set_window_size(slave_fd)
                self.process = subprocess.Popen(
                    self.command,
                    shell=True,
                    stdin=slave_fd,
                    stdout=slave_fd,
                    stderr=slave_fd,
                    start_new_session=True,
                    close_fds=True,
                    cwd=self.cwd,
                )
            finally:
                os.close(slave_fd)

            self.master_fd = master_fd
            self._stop_event.clear()
            self.reader_thread = threading.Thread(target=self._read_output, daemon=True)
            self.reader_thread.start()

    def _set_window_size(self, fd: int):
        winsize = struct.pack("HHHH", self.terminal_rows, self.terminal_cols, 0, 0)
        fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)

    def _read_output(self):
        try:
            while not self._stop_event.is_set():
                with self._lock:
                    master_fd = self.master_fd
                if master_fd is None:
                    break
                try:
                    data = os.read(master_fd, 4096)
                except OSError:
                    break
                if not data:
                    break
                self.output_queue.put(data.decode(errors="replace"))
        except Exception as e:
            logger.error(f"Error reading PTY output: {e}")

    def write_input(self, data: str):
        with self._lock:
            if self.master_fd is not None:
                try:
                    os.write(self.master_fd, data.encode())
                except OSError as e:
                    logger.error(f"Error writing to PTY: {e}")

    def suspend(self):
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGSTOP)
            except Exception as e:
                logger.error(f"Error suspending: {e}")

    def resume(self):
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGCONT)
            except Exception as e:
                logger.error(f"Error resuming: {e}")

    def kill(self):
        self._stop_event.set()
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
            except Exception:
                pass
        if self.master_fd is not None:
            try:
                os.close(self.master_fd)
            except Exception:
                pass
            self.master_fd = None

    def get_output(self, timeout: float = 0.1) -> str:
        output = ""
        try:
            while True:
                chunk = self.output_queue.get(timeout=timeout)
                output += chunk
        except queue.Empty:
            pass
        return output

    def is_alive(self) -> bool:
        return self.process is not None and self.process.poll() is None


# Example wrapper for claude / codex
def run_supervised_agent(agent_command: str, policy, grok_auditor, tui_callback=None, cwd=None):
    """
    High-level supervisor using PTY + policy + Grok.
    This is the "borrow" from gemOptq's real_agent_smoke + Pty + TUI concepts.
    Now supports real ContinuousEnforcer (pass observer/enforcer from caller for fs-observed effects).
    """
    from .enforcer import FileEffectObserver, ContinuousEnforcer
    runner = PtyAgentRunner(agent_command, cwd=cwd)
    runner.start()

    observer = FileEffectObserver(cwd or ".")
    observer.snapshot()
    enforcer = ContinuousEnforcer(policy=policy, observer=observer, grok_escalator=grok_auditor.grok if hasattr(grok_auditor, "grok") else None)

    try:
        enforcer.start()
        while runner.is_alive():
            output = runner.get_output()
            if output:
                # Real effects from observer + enforcer (not just text)
                decision = enforcer.check_once() or policy.evaluate([])
                if decision.action in (getattr(decision, "action", None),) and str(decision.action).lower() in ("review", "confirm"):
                    grok_dec = grok_auditor.audit("agent action", output)
                    if tui_callback:
                        tui_callback(decision, grok_dec, output)
                    # Wait for human or auto based on policy
                # Inject input if needed based on policy
    finally:
        enforcer.stop()
        runner.kill()
