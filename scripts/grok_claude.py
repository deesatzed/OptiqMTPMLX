#!/usr/bin/env python3
"""
grok-claude / .claude wrapper for Grok in the Loop + Sentinel supervision.

Borrowed concepts from gemOptq's real_agent_smoke.py (Claude trust prompt handling, PTY, disposable workspaces).

Usage:
  python scripts/grok_claude.py .
  # or after install: grok-claude .

This runs the 'claude' command (Claude Code) under full policy, enforcement, Grok escalation, and traces.
"""

import argparse
import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

# Assume installed or in path; adjust for dev
try:
    from nex.sentinel.pty_runner import PtyAgentRunner
    from nex.sentinel.policy import SentinelPolicy, FileEffect
    from nex.sentinel.grok_auditor import GrokAugmentedAuditor
    from nex.engine import Engine
except ImportError:
    # Dev path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from nex.sentinel.pty_runner import PtyAgentRunner
    from nex.sentinel.policy import SentinelPolicy, FileEffect
    from nex.sentinel.grok_auditor import GrokAugmentedAuditor
    from nex.engine import Engine


CLAUDE_TRUST_PROMPT = r"Quick.*safety.*check|No,.*exit|Enter.*confirm|Accessing.*workspace|Do you trust"


def main():
    parser = argparse.ArgumentParser(description="Run claude under Grok + Sentinel")
    parser.add_argument("workspace", nargs="?", default=".", help="Workspace to run in (disposable recommended)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--grok-in-loop", action="store_true", default=os.environ.get("GROK_IN_LOOP") == "true")
    args = parser.parse_args()

    if args.dry_run:
        print("DRY RUN: Would run 'claude .' under full Grok-in-the-Loop + Sentinel policy + traces.")
        print("Trust prompt would be intercepted and answered safely or escalated to Grok.")
        return

    # Use temp workspace for safety (borrow from gemOptq)
    with tempfile.TemporaryDirectory(prefix="grok-claude-") as tmp:
        cwd = Path(tmp) / "workspace"
        cwd.mkdir()
        # Copy or init minimal if needed; for demo, just run in temp

        cmd = f"claude {shlex.quote(args.workspace)}"
        print(f"Starting supervised: {cmd} (cwd={cwd})")
        print("Policy: Sentinel (protected paths, secrets, etc.) + Grok escalation for reviews.")
        print("Press Ctrl-C to kill. All actions traced.")

        runner = PtyAgentRunner(cmd, cwd=str(cwd))
        runner.start()

        engine = Engine()  # local OptiQ
        policy = SentinelPolicy()  # from ported
        auditor = GrokAugmentedAuditor(engine, use_grok=args.grok_in_loop)

        try:
            while runner.is_alive():
                output = runner.get_output(timeout=0.5)
                if output:
                    print(f"[AGENT] {output.strip()[:200]}")

                    # Simple effect detection (expand with real FileEffectObserver)
                    effects = []
                    if ".env" in output or "secret" in output.lower():
                        effects.append(FileEffect("write", ".env"))

                    decision = policy.evaluate(effects)
                    print(f"[POLICY] {decision.action.value}: {decision.reason}")

                    if decision.action in ("review", "confirm") or "trust" in output.lower():
                        if args.grok_in_loop:
                            grok_dec = auditor.audit("Claude Code action", output, risk=decision.risk)
                            print(f"[GROK] Escalated: {grok_dec}")
                            if grok_dec.get("verdict") == "block":
                                print("[GROK] BLOCK recommended. Injecting safe response.")
                                runner.write_input("n\n")  # safe default
                                continue

                        # Human in loop (in full TUI this would be rich approval)
                        print("[HUMAN] Review needed. Approve? (y/n/o for override)")
                        # For script: auto-safe for demo
                        user_input = input().strip().lower() or "n"
                        runner.write_input(user_input + "\n")

                    # Detect and handle Claude trust prompt specifically (borrowed pattern)
                    if re.search(CLAUDE_TRUST_PROMPT, output, re.I):
                        print("[SENTINEL] Claude trust prompt detected. Answering safely or escalating.")
                        runner.write_input("n\n")  # "No, exit" for safety, or let Grok decide

        except KeyboardInterrupt:
            print("\n[SENTINEL] Interrupted by user. Killing agent.")
        finally:
            runner.kill()
            print("[SENTINEL] Session ended. Check traces for full audit (local + Grok decisions).")


if __name__ == "__main__":
    main()