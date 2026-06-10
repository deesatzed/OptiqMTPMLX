"""
MCP Server for the Nex model.

Other AIs (Claude Desktop, Cursor, Windsurf, custom agents, etc.) can call this local
high-quality Apple-Silicon-optimized model as a tool via the Model Context Protocol.

Run with:
    source .venv/bin/activate
    nex mcp
    # or
    python -m nex.mcp

Typical Claude Desktop config (claude_desktop_config.json):

{
  "mcpServers": {
    "nex-local": {
      "command": "/absolute/path/to/nex-n2-mlx-run/.venv/bin/python",
      "args": ["-m", "nex.mcp"],
      "cwd": "/absolute/path/to/nex-n2-mlx-run",
      "env": {}
    }
  }
}

The server exposes these tools:

- nex_ask
- nex_chat_turn  (stateful across calls using session_id)
- nex_list_sessions
- nex_get_history
- nex_create_session
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from . import DEFAULT_MODEL
from .engine import Engine
from .models import KNOWN_MODELS, get_default_model, get_profile, list_profiles
from .persistence import (
    SessionRecord,
    get_latest_session,
    list_sessions,
    load_session,
    new_session_id,
    save_session,
)
from .tools import inject_tool_instructions  # reuse for optional agentic behavior

# Create the MCP server instance
mcp = FastMCP(
    name="nex-local",
    instructions=(
        "High-performance local LLM runner for the OptiQ-4bit MLX model family "
        "(Qwen3/3.5/3.6, Gemma-4, Nemotron, Nex-N2, MiniCPM, etc.). "
        "All models run locally on Apple Silicon via mlx-lm. "
        "Use the `model` parameter on tools to switch models (e.g. qwen3.5-9b, gemma-4-12b, nemotron-nano-4b)."
    ),
)

# Shared engine (lazy loaded on first tool use)
_engine: Optional[Engine] = None


def _get_engine(
    model: Optional[str] = None,
    enable_mtp: bool = False,
    draft_model: Optional[str] = None,
    num_draft_tokens: int = 3,
) -> Engine:
    global _engine
    resolved = model or get_default_model()
    profile = get_profile(resolved)
    resolved = profile.repo_id

    final_draft = draft_model
    if enable_mtp and not final_draft:
        if profile and profile.supports_mtp and profile.mtp_repo_id:
            final_draft = profile.mtp_repo_id

    if (
        _engine is None
        or _engine.model_id != resolved
        or _engine.draft_model_id != final_draft
    ):
        _engine = Engine(
            model_id=resolved,
            draft_model_id=final_draft,
            num_draft_tokens=num_draft_tokens,
        )
        _engine.load()
    return _engine


@mcp.tool()
def nex_ask(
    prompt: str,
    system: Optional[str] = None,
    max_tokens: int = 1024,
    temperature: float = 0.7,
    top_p: float = 0.95,
    model: Optional[str] = None,
    enable_mtp: bool = False,
    draft_model: Optional[str] = None,
    num_draft_tokens: int = 3,
) -> Dict[str, Any]:
    """
    One-shot generation with the local model (supports any registered OptiQ/MLX model).

    Args:
        prompt: The user prompt / question / instruction.
        system: Optional system prompt.
        max_tokens: Maximum new tokens to generate.
        temperature: Sampling temperature (lower = more deterministic).
        top_p: Nucleus sampling.
        model: Model key/alias/repo (e.g. qwen9b, gemma12b, or full HF id).
        enable_mtp: Enable Multi-Token Prediction / speculative decoding for speedup.
        draft_model: Explicit draft model for MTP.
        num_draft_tokens: Draft tokens for speculative decoding.

    Returns:
        dict with 'text' and 'stats'.
    """
    engine = _get_engine(model, enable_mtp, draft_model, num_draft_tokens)
    full_prompt = engine.apply_chat_template(
        ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}],
        add_generation_prompt=True,
    )

    text = ""
    final_stats = None
    for chunk, stats in engine.stream_generate(
        full_prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
    ):
        if chunk:
            text += chunk
        if stats:
            final_stats = stats

    return {
        "text": text.strip(),
        "model": model,
        "stats": final_stats.__dict__ if final_stats else {},
    }


@mcp.tool()
def nex_create_session(
    system: Optional[str] = None,
    session_id: Optional[str] = None,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """Create (or reuse) a named session for multi-turn conversation."""
    sid = session_id or new_session_id("mcp")
    rec = SessionRecord(session_id=sid, model=model)
    if system:
        rec.system_prompt = system
    save_session(rec)
    return {"session_id": sid, "system": rec.system_prompt, "created": True}


@mcp.tool()
def nex_chat_turn(
    session_id: str,
    prompt: str,
    max_tokens: int = 1024,
    temperature: float = 0.7,
    top_p: float = 0.95,
    model: Optional[str] = None,
    enable_mtp: bool = False,
    draft_model: Optional[str] = None,
    num_draft_tokens: int = 3,
) -> Dict[str, Any]:
    """
    Continue (or start) a multi-turn chat session.

    The session keeps full message history and uses the model's native chat template.
    Perfect for longer coding sessions, debugging, planning, or iterative refinement.

    Returns the assistant's response plus updated stats.
    """
    engine = _get_engine(model, enable_mtp, draft_model, num_draft_tokens)
    rec = load_session(session_id)
    if rec is None:
        rec = SessionRecord(session_id=session_id, model=model)

    # Add user message
    rec.messages.append({"role": "user", "content": prompt})

    # Build prompt from full history
    chat_prompt = engine.apply_chat_template(
        ([{"role": "system", "content": rec.system_prompt}] if rec.system_prompt else []) + rec.messages,
        add_generation_prompt=True,
    )

    text = ""
    final_stats = None
    for chunk, stats in engine.stream_generate(
        chat_prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
    ):
        if chunk:
            text += chunk
        if stats:
            final_stats = stats

    # Append assistant reply
    rec.messages.append({"role": "assistant", "content": text.strip()})
    save_session(rec)

    return {
        "text": text.strip(),
        "session_id": session_id,
        "history_length": len(rec.messages),
        "stats": final_stats.__dict__ if final_stats else {},
    }


@mcp.tool()
def nex_list_sessions(limit: int = 10) -> List[Dict[str, Any]]:
    """List recent persisted chat / agent sessions (most recent first)."""
    recs = list_sessions(limit=limit)
    return [
        {
            "session_id": r.session_id,
            "model": r.model,
            "created_at": r.created_at,
            "updated_at": r.updated_at,
            "message_count": len(r.messages),
        }
        for r in recs
    ]


@mcp.tool()
def nex_get_history(session_id: str) -> Dict[str, Any]:
    """Retrieve full message history for a session (useful for context or debugging)."""
    rec = load_session(session_id)
    if rec is None:
        return {"error": f"Session not found: {session_id}"}
    return {
        "session_id": rec.session_id,
        "system_prompt": rec.system_prompt,
        "messages": rec.messages,
        "params": rec.params,
    }


@mcp.tool()
def nex_list_models(
    family: Optional[str] = None,
    size_class: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """List available high-quality OptiQ and MLX models known to this runner (with aliases and recommendations)."""
    from .models import list_profiles

    profiles = list_profiles(family=family, size_class=size_class)
    return [
        {
            "key": None,
            "name": p.name,
            "repo_id": p.repo_id,
            "family": p.family,
            "size_class": p.size_class,
            "params": p.params,
            "strengths": p.strengths,
            "recommended_temperature": p.recommended_temperature,
            "recommended_max_tokens": p.recommended_max_tokens,
            "supports_mtp": p.supports_mtp,
            "aliases": p.aliases,
            "notes": p.notes,
        }
        for p in profiles
    ]


@mcp.tool()
def nex_search_history(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Semantic search over your previous conversations (requires the 'rag' extra)."""
    try:
        from .history_rag import search_history
        return search_history(query, top_k=top_k)
    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool()
def nex_run_agent(
    goal: str,
    max_steps: int = 10,
    temperature: float = 0.4,
    model: Optional[str] = None,
    enable_mtp: bool = False,
    draft_model: Optional[str] = None,
    num_draft_tokens: int = 3,
) -> Dict[str, Any]:
    """
    Run a short autonomous agent loop with safe built-in tools (file ops + code execution in sandbox).

    The agent can list/read/write files, run Python, and execute limited shell commands
    inside a protected ./sandbox directory. Great for "build this small thing", "analyze that data",
    or "write + test a script" style tasks that the host AI wants the local model to drive.

    Supports MTP for faster agent steps.

    Returns the final answer and number of steps taken.
    """
    from .agent import run_agent as _run_agent_impl
    from .engine import Engine as _Engine

    eng = _Engine(
        model_id=model or get_default_model(),
        draft_model_id=draft_model,
        num_draft_tokens=num_draft_tokens,
    )
    result = _run_agent_impl(
        goal=goal,
        engine=eng,
        max_steps=max_steps,
        temperature=temperature,
    )
    return {
        "session_id": result.session_id,
        "final_answer": result.final_answer,
        "steps": result.steps,
        "stats_summary": [s.__dict__ for s in result.stats],
    }


def run_server():
    """Entry point for `python -m nex.mcp` or `nex mcp`."""
    # FastMCP handles stdio transport automatically when run this way
    mcp.run()


if __name__ == "__main__":
    run_server()
