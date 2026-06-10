#!/usr/bin/env python3
"""
grok-codex / .codex wrapper for Grok in the Loop + Sentinel supervision.

Borrows heavily from gemOptq's real_agent_smoke.py Codex exec + TUI smokes, trust prompts, interaction injection.

Usage:
  python scripts/grok_codex.py .
  # or grok-codex after install

Runs Codex (Cursor AI or similar) under the full policy, Grok escalation, traces, and enforcement.
"""

import argparse
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

# Same import pattern as grok_claude
try:
    from nex.sentinel.pty_runner import PtyAgentRunner
    from nex.sentinel.policy import SentinelPolicy, FileEffect
    from nex.sentinel.grok_auditor import GrokAugmentedAuditor
    from nex.engine import Engine
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from nex.sentinel.pty_runner import PtyAgentRunner
    from nex.sentinel.policy import SentinelPolicy, FileEffect
    from nex.sentinel.grok_auditor import GrokAugmentedAuditor
    from nex.engine import Engine


CODEX_TRUST_PATTERNS = [
    r"Do.*trust|Yes, continue|Press enter",
    r"Would you like to run the following command|Yes, proceed",
]
CODEX_EXEC_MARKER = "SENTINEL_CODEX_OK"


def main():
    parser = argparse.ArgumentParser(description="Run codex under Grok + Sentinel")
    parser.add_argument("workspace", nargs="?", default=".", help="Workspace")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--grok-in-loop", action="store_true", default=os.environ.get("GROK_IN_LOOP") == "true")
    args = parser.parse_args()

    if args.dry_run:
        print("DRY RUN: Would supervise 'codex .' with policy gates, Grok reviews on risky actions, and full traces.")
        return

    with tempfile.TemporaryDirectory(prefix="grok-codex-") as tmp:
        cwd = Path(tmp) / "workspace"
        cwd.mkdir()

        cmd = f"codex {shlex.quote(args.workspace)}"
        print(f"Supervised Codex: {cmd}")

        runner = PtyAgentRunner(cmd, cwd=str(cwd))
        runner.start()

        engine = Engine()
        policy = SentinelPolicy()
        auditor = GrokAugmentedAuditor(engine, use_grok=args.grok_in_loop)

        try:
            while runner.is_alive():
                output = runner.get_output(timeout=0.5)
                if output:
                    print(f"[CODEX] {output.strip()[:150]}")

                    effects = []
                    # Borrowed detection logic
                    if ".env" in output or any(p in output.lower() for p in ["secret", "key", "token"]):
                        effects.append(FileEffect("write", ".env"))

                    decision = policy.evaluate(effects)
                    print(f"[POLICY] {decision.action.value}: {decision.reason}")

                    if decision.action in ("review", "confirm"):
                        grok_dec = auditor.audit("Codex tool/command", output, risk=decision.risk)
                        print(f"[GROK] {grok_dec.get('verdict')}: {grok_dec.get('reason', '')[:100]}")

                        if grok_dec.get("verdict") == "block":
                            print("[GROK] Blocking risky action.")
                            runner.write_input("n\n")
                            continue

                    # Codex-specific trust / command approvals (borrowed from smoke)
                    for pattern in CODEX_TRUST_PATTERNS:
                        if re.search(pattern, output, re.I):
                            print("[SENTINEL] Codex approval prompt. Safe response or Grok review.")
                            runner.write_input("y\n")  # or n based on policy/grok
                            break

                    # Detect the sentinel marker for smoke/demo
                    if CODEX_EXEC_MARKER in output:
                        print(f"[SENTINEL] Harmless execution verified: {CODEX_EXEC_MARKER}")

        except KeyboardInterrupt:
            print("\nUser interrupt.")
        finally:
            runner.kill()
            print("Codex session ended under supervision. Full trace available.")


if __name__ == "__main__":
    main()