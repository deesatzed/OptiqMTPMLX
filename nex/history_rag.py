"""
Minimal semantic search over chat history (optional 'rag' extra).

Usage:
    from nex.history_rag import search_history
    results = search_history("how did I implement the parser?")
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Tuple

from .persistence import LOGS_DIR, SESSIONS_DIR


def _load_all_turns() -> List[Tuple[str, str, str]]:
    """Load (session_id, role, content) from logs and sessions."""
    turns = []
    # From JSONL logs
    for log_file in LOGS_DIR.glob("nex-*.jsonl"):
        for line in log_file.read_text().splitlines():
            try:
                entry = json.loads(line)
                if "content" in entry and entry.get("role") in ("user", "assistant"):
                    turns.append((
                        entry.get("session_id", "unknown"),
                        entry["role"],
                        entry["content"][:2000]
                    ))
            except Exception:
                pass

    # From session JSONs
    for sess_file in SESSIONS_DIR.glob("*.json"):
        try:
            data = json.loads(sess_file.read_text())
            sid = data.get("session_id", sess_file.stem)
            for msg in data.get("messages", []):
                if msg.get("role") in ("user", "assistant"):
                    turns.append((sid, msg["role"], msg["content"][:2000]))
        except Exception:
            pass
    return turns


def search_history(query: str, top_k: int = 5) -> List[dict]:
    """Very lightweight semantic search (requires sentence-transformers)."""
    try:
        from sentence_transformers import SentenceTransformer, util
        import torch
    except ImportError:
        return [{"error": "Install with: pip install -e '.[rag]'"}]

    model = SentenceTransformer("all-MiniLM-L6-v2")
    turns = _load_all_turns()
    if not turns:
        return []

    docs = [t[2] for t in turns]
    embeddings = model.encode(docs, convert_to_tensor=True)
    query_emb = model.encode(query, convert_to_tensor=True)

    scores = util.cos_sim(query_emb, embeddings)[0]
    top_results = torch.topk(scores, min(top_k, len(scores)))

    results = []
    for score, idx in zip(top_results[0], top_results[1]):
        sid, role, content = turns[int(idx)]
        results.append({
            "session_id": sid,
            "role": role,
            "content": content[:600],
            "score": float(score),
        })
    return results