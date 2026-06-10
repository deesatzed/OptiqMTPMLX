"""
ContinuousEnforcer ported/adapted from gemOptq/src/sentinel/enforcer.py

Provides continuous monitoring and rollback for protected file effects in the sandbox.
Integrates with Nex's agent sandbox and Grok escalation.
"""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable
from typing import Optional, List, Dict

from .policy import SentinelPolicy, PolicyAction, PolicyDecision, FileEffect
from ..tools import TOOLS  # to hook into sandbox effects

logger = logging.getLogger(__name__)


class FileEffectObserver:
    """Simple observer for sandbox effects. In real use, integrate with actual file ops in tools."""
    def __init__(self, workspace_root: str = "sandbox"):
        self.workspace_root = workspace_root
        self.baseline: Dict[str, str] = {}

    def snapshot(self):
        # Placeholder - in full integration, walk the sandbox dir
        pass

    def diff(self) -> List[FileEffect]:
        # Placeholder - return detected created/modified/deleted in sandbox
        # For demo, return empty; real integration would use os.walk or watchdog
        return []

    def safe_path(self, path: str):
        # Ensure within sandbox
        return path  # simplified


class ContinuousEnforcer:
    def __init__(
        self,
        *,
        policy: SentinelPolicy,
        observer: FileEffectObserver,
        interval_seconds: float = 0.5,
        on_block: Optional[Callable[[PolicyDecision, List[FileEffect]], None]] = None,
        grok_escalator: Optional[object] = None,  # GrokEscalator instance
    ):
        self.policy = policy
        self.observer = observer
        self.interval_seconds = interval_seconds
        self.on_block = on_block
        self.grok_escalator = grok_escalator
        self.last_decision: Optional[PolicyDecision] = None
        self.last_effects: List[FileEffect] = []
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def start(self):
        with self._lock:
            if self._thread and self._thread.is_alive():
                raise RuntimeError("ContinuousEnforcer already active")
            self.observer.snapshot()
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def stop(self):
        with self._lock:
            self._stop_event.set()
            thread = self._thread
            self._thread = None
        if thread:
            thread.join(timeout=2)

    def check_once(self) -> Optional[PolicyDecision]:
        effects = self.observer.diff()
        if not effects:
            return None

        decision = self.policy.evaluate(effects)
        self.last_decision = decision
        self.last_effects = effects

        if decision.action is PolicyAction.BLOCK:
            # In real: suspend runner, rollback
            if self.on_block:
                self.on_block(decision, effects)
            return decision

        # If Grok escalation configured and REVIEW
        if self.grok_escalator and decision.action is PolicyAction.REVIEW and self.grok_escalator.is_available():
            grok_dec = self.grok_escalator.escalate(
                intent="Continuous enforcement review",
                effects=[{"operation": e.operation, "path": e.path} for e in effects],
                local_verdict="review",
                local_reason=decision.reason,
            )
            decision.grok_escalated = True
            decision.grok_verdict = grok_dec.get("verdict")
            if grok_dec.get("verdict") == "block":
                decision.action = PolicyAction.BLOCK
                decision.reason = f"Grok escalated: {grok_dec.get('reason')}"

        self.observer.snapshot()
        return decision

    def _run(self):
        while not self._stop_event.is_set():
            try:
                self.check_once()
            except Exception as e:
                logger.error(f"Continuous enforcement failed: {e}")
            self._stop_event.wait(self.interval_seconds)


# Factory to create with Nex sandbox integration
def create_sandbox_enforcer(sandbox_path: str = "sandbox", **kwargs):
    observer = FileEffectObserver(sandbox_path)
    # policy would be passed in
    return ContinuousEnforcer(observer=observer, **kwargs)