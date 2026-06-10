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

        # Real ContinuousEnforcer + observer (hardened gain — real fs effects, not just text)
        from nex.sentinel.enforcer import FileEffectObserver, ContinuousEnforcer
        observer = FileEffectObserver(str(cwd))
        observer.snapshot()
        enforcer = ContinuousEnforcer(
            policy=policy,
            observer=observer,
            grok_escalator=auditor.grok if hasattr(auditor, "grok") else None
        )
        enforcer.start()

        # Real counters (for the needs-based end report that proves the wrapper value)
        grok_escalations = 0
        blocks = 0
        reviews = 0
        t0 = __import__("time").time()

        try:
            while runner.is_alive():
                output = runner.get_output(timeout=0.5)
                if output:
                    print(f"[AGENT] {output.strip()[:200]}")

                    # Real effects via ContinuousEnforcer (hardened gain)
                    decision = enforcer.check_once() or policy.evaluate([])
                    print(f"[POLICY] {decision.action.value}: {decision.reason}")

                    if decision.action in ("review", "confirm") or "trust" in output.lower():
                        grok_escalations += 1
                        if args.grok_in_loop:
                            grok_dec = auditor.audit("Claude Code action", output, risk=decision.risk)
                            print(f"[GROK] Escalated: {grok_dec}")
                            if grok_dec.get("verdict") == "block":
                                blocks += 1
                                print("[GROK] BLOCK recommended. Injecting safe response.")
                                runner.write_input("n\n")  # safe default
                                continue
                            else:
                                reviews += 1

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
            enforcer.stop()
            runner.kill()
            wall = __import__("time").time() - t0
            print("\n=== Grok-in-the-Loop Claude Supervision Report (needs-based proof) ===")
            print(f"Session wall: {wall:.1f}s | Grok escalations: {grok_escalations} | Blocks: {blocks} | Reviews: {reviews}")
            print("External Claude ran under Sentinel policy + Grok auditor + trust injection + real ContinuousEnforcer.")
            print("Full audit in traces. This is the 'keep my daily driver, make it safe + smart' capability no one else ships.")
            print("[SENTINEL] Session ended. Check traces for full audit (local + Grok decisions).")


if __name__ == "__main__":
    main()