"""Autonomous agent loop with tool use for the Nex model.

Usage from CLI:
    nex agent "Create a small FastAPI hello world in the sandbox and test it with run_python"
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel

from .engine import Engine, GenerationStats
from .models import get_profile
from .persistence import SessionRecord, log_turn, new_session_id, save_session
from .tools import (
    execute_tool,
    format_observation,
    inject_tool_instructions,
    load_plugins,
    parse_tool_call,
)

console = Console()


@dataclass
class AgentResult:
    session_id: str
    final_answer: str
    steps: int
    stats: List[GenerationStats]


def run_agent(
    goal: str,
    *,
    engine: Engine,
    system_prompt: Optional[str] = None,
    max_steps: int = 12,
    max_tokens: int = 1536,
    temperature: float = 0.4,
    session_id: Optional[str] = None,
    persist: bool = True,
) -> AgentResult:
    """
    Run a ReAct-style autonomous agent loop until the model produces a final answer
    without emitting a tool call, or max_steps is reached.
    """
    load_plugins()

    sid = session_id or new_session_id("agent")
    record = SessionRecord(session_id=sid, model=engine.model_id)

    # Model-aware tool instructions
    profile = get_profile(engine.model_id)
    base_instructions = inject_tool_instructions(system_prompt)
    if profile and profile.agent_tool_instructions:
        tool_section = profile.agent_tool_instructions
    else:
        tool_section = ""
    record.system_prompt = base_instructions + ("\n\n" + tool_section if tool_section else "")

    record.params = {
        "temperature": temperature,
        "top_p": 0.9,
        "max_tokens": max_tokens,
    }

    messages: List[dict] = [{"role": "system", "content": record.system_prompt}]
    messages.append({"role": "user", "content": goal})

    # Strong format reminder on the first turn (many small models need this)
    messages.append({
        "role": "user",
        "content": "REMINDER: Use ONLY the exact format shown in the system prompt. Example of a correct first action:\ncall tool list_dir with path is .\n\nDo not explain the format in your thinking — just emit a clean tool call when you want to use a tool."
    })

    if persist:
        save_session(record)

    console.print(Panel.fit(f"[bold]Agent Goal[/bold]\n{goal}", border_style="magenta"))
    console.print(f"[dim]Session: {sid} | max_steps={max_steps}[/dim]\n")

    steps = 0
    all_stats: List[GenerationStats] = []

    while steps < max_steps:
        steps += 1
        prompt = engine.apply_chat_template(messages, add_generation_prompt=True)

        console.print(f"[bold cyan]Step {steps}[/bold cyan] — thinking + possible tool use...")

        full_text = ""
        final_stats: Optional[GenerationStats] = None

        for chunk, stats in engine.stream_generate(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9,
        ):
            if chunk:
                full_text += chunk
            if stats:
                final_stats = stats

        if final_stats:
            all_stats.append(final_stats)

        # Log the assistant turn
        log_turn(
            session_id=sid,
            model=engine.model_id,
            role="assistant",
            content=full_text,
            stats=final_stats.__dict__ if final_stats else None,
            extra={"step": steps, "mode": "agent"},
        )

        # Check for tool call
        tool_call = parse_tool_call(full_text)

        # Append the model's output to history (we keep the raw thinking + call for transparency)
        messages.append({"role": "assistant", "content": full_text})

        if tool_call:
            tool_name = tool_call["name"]
            console.print(f"[yellow]→ Tool call:[/yellow] {tool_name} {tool_call.get('arguments', {})}")

            observation = execute_tool(tool_call)
            obs_text = format_observation(tool_name, observation)

            console.print(f"[green]← Observation:[/green] {observation[:300]}{'...' if len(observation) > 300 else ''}\n")

            messages.append({"role": "user", "content": obs_text})

            log_turn(
                session_id=sid,
                model=engine.model_id,
                role="tool",
                content=obs_text,
                extra={"tool": tool_name, "step": steps},
            )

            if persist:
                record.messages = messages
                save_session(record)
            continue

        # No tool call — this is the final answer (or the model decided to respond)
        # Clean up any remaining think tags for presentation
        final = full_text
        console.print(Panel(final.strip(), title=f"Final response (step {steps})", border_style="green"))

        if persist:
            record.messages = messages
            save_session(record)

        return AgentResult(
            session_id=sid,
            final_answer=final.strip(),
            steps=steps,
            stats=all_stats,
        )

    # Max steps reached
    last = messages[-1]["content"] if messages else ""
    console.print(f"[red]Max steps ({max_steps}) reached.[/red]")
    return AgentResult(
        session_id=sid,
        final_answer=last,
        steps=steps,
        stats=all_stats,
    )
