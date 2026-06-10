"""
Unified Trace Viewer.

Can replay traces from the Nex persistence or gemOptq-style JSONL.
Shows local vs Grok decisions.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict


def replay_trace(trace_path: str, format: str = "text") -> List[Dict]:
    """Simple unified replay. Returns list of events."""
    path = Path(trace_path)
    events = []
    if not path.exists():
        return [{"error": f"Trace not found: {trace_path}"}]

    with open(path) as f:
        for line in f:
            try:
                event = json.loads(line.strip())
                events.append(event)
            except:
                pass

    if format == "text":
        for e in events:
            ts = e.get("ts", "")
            role = e.get("role", "")
            content = str(e.get("content", ""))[:120]
            grok = " [GROK]" if "grok" in str(e).lower() else ""
            print(f"{ts} | {role}{grok}: {content}")
    return events


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        replay_trace(sys.argv[1])