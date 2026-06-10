"""Persistence for sessions (JSON) and JSONL logging."""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import DEFAULT_MODEL

BASE_DIR = Path(__file__).resolve().parents[1]  # nex-n2-mlx-run/
SESSIONS_DIR = BASE_DIR / "sessions"
LOGS_DIR = BASE_DIR / "logs"

SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class SessionRecord:
    session_id: str
    model: str = DEFAULT_MODEL
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    system_prompt: Optional[str] = None
    messages: List[Dict[str, str]] = field(default_factory=list)
    params: Dict[str, Any] = field(default_factory=lambda: {"temperature": 0.7, "top_p": 0.95, "max_tokens": 1024})

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "SessionRecord":
        return cls(**d)


def _session_path(session_id: str) -> Path:
    safe = "".join(c for c in session_id if c.isalnum() or c in "-_")[:64]
    return SESSIONS_DIR / f"{safe}.json"


def save_session(record: SessionRecord) -> Path:
    record.updated_at = datetime.utcnow().isoformat() + "Z"
    path = _session_path(record.session_id)
    path.write_text(json.dumps(record.to_dict(), indent=2))
    return path


def load_session(session_id: str) -> Optional[SessionRecord]:
    path = _session_path(session_id)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        return SessionRecord.from_dict(data)
    except Exception:
        return None


def list_sessions(limit: int = 20) -> List[SessionRecord]:
    files = sorted(SESSIONS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    recs: List[SessionRecord] = []
    for f in files[:limit]:
        try:
            recs.append(SessionRecord.from_dict(json.loads(f.read_text())))
        except Exception:
            continue
    return recs


def get_latest_session() -> Optional[SessionRecord]:
    recs = list_sessions(1)
    return recs[0] if recs else None


def new_session_id(prefix: str = "chat") -> str:
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    return f"{prefix}-{ts}"


# ---------------- JSONL Logging ----------------

def log_turn(
    *,
    session_id: str,
    model: str,
    role: str,
    content: str,
    stats: Optional[Dict[str, Any]] = None,
    extra: Optional[Dict[str, Any]] = None,
):
    """Append one turn to daily JSONL log."""
    day = datetime.utcnow().strftime("%Y%m%d")
    log_file = LOGS_DIR / f"nex-{day}.jsonl"
    entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "session_id": session_id,
        "model": model,
        "role": role,
        "content": content[:8000],  # truncate very long content
    }
    if stats:
        entry["stats"] = stats
    if extra:
        entry.update(extra)
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def get_log_path_for_today() -> Path:
    day = datetime.utcnow().strftime("%Y%m%d")
    return LOGS_DIR / f"nex-{day}.jsonl"
