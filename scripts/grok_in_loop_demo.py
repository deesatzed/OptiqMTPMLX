#!/usr/bin/env python
"""
Grok in the Loop Demo

Run a small autonomous task under the new hybrid local + Grok escalation.

Usage:
    GROK_IN_LOOP=true python scripts/grok_in_loop_demo.py

Requires XAI_API_KEY for full escalation.
"""

import os
from nex.agent import run_agent
from nex.engine import Engine

def main():
    print("=== Grok in the Loop Demo ===")
    print("This runs a tiny agent task. With GROK_IN_LOOP=true it will escalate risky steps to Grok.\n")

    engine = Engine()  # defaults to Nex or configured model
    result = run_agent(
        goal="Create a small hello.txt in the sandbox with the text 'Grok in the Loop works!' and verify it.",
        engine=engine,
        max_steps=5,
        temperature=0.3,
    )

    print("\n=== Result ===")
    print(f"Session: {result.session_id}")
    print(f"Steps taken: {result.steps}")
    print(f"Final answer:\n{result.final_answer}")

    if os.environ.get("GROK_IN_LOOP"):
        print("\n(Note: Grok escalation was enabled. Check the trace for 'grok-escalation' entries.)")


if __name__ == "__main__":
    main()