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


def export_gallery(sessions_dir: str = "sessions", logs_dir: str = "logs", out: str | None = None, redact: bool = True, format: str = "md") -> str:
    """
    Public redacted trace gallery generator (needs-based for audit/share/compliance/"make Elon proud" demos).
    Scans real persisted sessions + JSONL logs, extracts oversight-like summaries (grok escalations, policy decisions, effects),
    produces self-contained shareable output (MD table or minimal HTML). Redacts obvious secrets.
    Real data only. No new deps.
    """
    from pathlib import Path
    import json, re
    sdir = Path(sessions_dir)
    ldir = Path(logs_dir)
    items = []
    # sessions
    for p in sorted(sdir.glob("*.json"))[:20]:
        try:
            data = json.loads(p.read_text())
            sid = data.get("session_id", p.stem)
            msgs = data.get("messages", [])
            grok_count = sum(1 for m in msgs if "grok" in str(m).lower() or "escalat" in str(m).lower())
            items.append({"id": sid, "type": "session", "msgs": len(msgs), "grok": grok_count, "source": str(p)})
        except:
            pass
    # logs (JSONL)
    for lp in sorted(ldir.glob("*.jsonl"))[:10]:
        try:
            cnt = 0
            grok = 0
            with open(lp) as f:
                for line in f:
                    cnt += 1
                    if "grok" in line.lower() or "escalat" in line.lower():
                        grok += 1
            items.append({"id": lp.stem, "type": "log", "msgs": cnt, "grok": grok, "source": str(lp)})
        except:
            pass

    def _redact(t: str) -> str:
        if not redact:
            return t
        t = re.sub(r'(?i)(key|token|secret|password)[\s:=]+[\S]+', r'\1=***REDACTED***', t)
        return t[:200]

    lines = ["# Grok-in-the-Loop Trace Gallery (redacted, shareable)", "", "| ID | Type | Events | Grok escalations | Source |", "|---|---|---|---|---|"]
    for it in items:
        lines.append(f"| {_redact(it['id'])} | {it['type']} | {it['msgs']} | {it['grok']} | {it['source']} |")
    lines.append("\n*Generated from real sessions/logs. Each entry has full replay via `nex trace replay <id>`. Use for team review, compliance, or demos.*")
    content = "\n".join(lines)

    if out:
        Path(out).write_text(content)
        print(f"Gallery written to {out}")
    else:
        print(content)
    return content


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        replay_trace(sys.argv[1])
    else:
        export_gallery()