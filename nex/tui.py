"""
SOTA Textual TUI for Nex.

Launch with:
    nex tui
    ./run.sh tui
    nex chat --tui

Features:
- Beautiful reactive terminal UI (modern dark theme)
- Live model switching from the registry (including MTP variants)
- MTP toggle
- Session sidebar
- Streaming chat with think-tag awareness
- Live stats panel (tokens/s, peak memory, MTP active)
- Keyboard-first (Ctrl+Q to quit, etc.)

This complements the fast Typer CLI. Textual gives a much more "app-like" aesthetic experience.
"""

from __future__ import annotations

import asyncio
from typing import Optional

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListView,
    ListItem,
    Log,
    Markdown,
    Static,
    Switch,
)

from .engine import Engine
from .models import get_default_model, get_profile, list_profiles
from .render import ThinkAwareStreamer  # reuse our think logic where possible


class NexTUI(App):
    """Modern TUI for the multi-model OptiQ runner."""

    CSS = """
    Screen {
        background: $surface;
    }

    #sidebar {
        width: 28;
        background: $panel;
        border-right: thick $primary;
    }

    #chat_log {
        height: 1fr;
        border: round $accent;
        padding: 1;
        overflow-y: auto;
    }

    #input {
        dock: bottom;
        margin: 1 0;
    }

    #stats {
        height: 5;
        background: $boost;
        border: round $secondary;
        padding: 0 1;
    }

    .model-item {
        padding: 0 1;
    }

    .active {
        background: $accent;
        color: $text;
    }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("ctrl+m", "switch_model", "Switch Model"),
        Binding("ctrl+t", "toggle_mtp", "Toggle MTP"),
        Binding("ctrl+l", "clear_chat", "Clear"),
    ]

    current_model: reactive[str] = reactive(get_default_model())
    mtp_enabled: reactive[bool] = reactive(False)
    stats_text: reactive[str] = reactive("Ready")

    def __init__(self):
        super().__init__()
        self.engine: Optional[Engine] = None
        self.messages: list[dict] = []
        self._streamer = ThinkAwareStreamer(show_thinking=True)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal():
            with Vertical(id="sidebar"):
                yield Label("Models", classes="title")
                yield ListView(id="model_list")
                yield Label("Sessions (stub)", classes="title")
                yield ListView(id="session_list")
                yield Static("MTP", id="mtp_label")
                yield Switch(value=self.mtp_enabled, id="mtp_switch")

            with Vertical():
                yield Log(id="chat_log", highlight=True, wrap=True)
                yield Input(placeholder="Type a message... (Enter to send, Ctrl+Q to quit)", id="input")
                yield Static(self.stats_text, id="stats")

        yield Footer()

    def on_mount(self) -> None:
        self.title = "Nex • Multi-Model OptiQ TUI"
        self.sub_title = "Apple Silicon • MTP ready"
        self._load_models()
        self._load_engine()
        self.query_one("#input", Input).focus()

    def _load_models(self) -> None:
        model_list = self.query_one("#model_list", ListView)
        model_list.clear()

        profiles = list_profiles()
        for p in profiles:
            item = ListItem(Label(f"{p.name} ({p.family})"), name=p.repo_id)
            if p.repo_id == self.current_model:
                item.add_class("active")
            model_list.append(item)

    def _load_engine(self) -> None:
        draft = None
        if self.mtp_enabled:
            profile = get_profile(self.current_model)
            if profile.supports_mtp and profile.mtp_repo_id:
                draft = profile.mtp_repo_id

        self.engine = Engine(
            model_id=self.current_model,
            draft_model_id=draft,
            num_draft_tokens=3,
        )
        # Lazy load happens on first generate
        self.stats_text = f"Model: {get_profile(self.current_model).name}"
        if draft:
            self.stats_text += " + MTP"
        self.query_one("#stats", Static).update(self.stats_text)

    def watch_mtp_enabled(self, enabled: bool) -> None:
        self._load_engine()

    def on_switch_changed(self, event: Switch.Changed) -> None:
        if event.switch.id == "mtp_switch":
            self.mtp_enabled = event.value

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id == "model_list" and event.item and event.item.name:
            new_model = event.item.name
            if new_model != self.current_model:
                self.current_model = new_model
                # Rebuild list highlighting
                self._load_models()
                self._load_engine()
                self.query_one("#chat_log", Log).write_line(f"[dim]Switched to {get_profile(new_model).name}[/dim]")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text or not self.engine:
            return

        event.input.value = ""

        log = self.query_one("#chat_log", Log)
        log.write_line(f"[bold green]You[/bold green]: {text}")

        # Simple streaming simulation (run generation in a worker)
        self.run_worker(self._generate_response(text, log), exclusive=True)

    async def _generate_response(self, prompt: str, log: Log) -> None:
        if not self.engine:
            return

        # Build a minimal prompt (for demo we skip full session history)
        try:
            # For real multi-turn we would use the ChatSession + apply_chat_template
            # Here we do a quick one-shot for the TUI demo
            formatted = prompt  # In a full version: self.engine.apply_chat_template(...)

            log.write_line("[bold cyan]Nex[/bold cyan]: ")

            full_response = []
            for chunk, stats in self.engine.stream_generate(
                formatted,
                max_tokens=512,
                temperature=0.7,
            ):
                if chunk:
                    full_response.append(chunk)
                    # Simple append (real TUI would use a better live widget)
                    log.write(chunk, scroll_end=True)

                if stats:
                    self.stats_text = (
                        f"gen: {stats.generation_tokens} tok @ {stats.generation_tps:.1f} t/s  "
                        f"peak: {stats.peak_memory_gb:.1f} GB"
                    )
                    if self.mtp_enabled:
                        self.stats_text += "  [MTP]"
                    self.query_one("#stats", Static).update(self.stats_text)

            # After generation
            response_text = "".join(full_response)
            log.write_line("")  # newline

        except Exception as e:
            log.write_line(f"[red]Error: {e}[/red]")

    def action_toggle_mtp(self) -> None:
        switch = self.query_one("#mtp_switch", Switch)
        switch.value = not switch.value
        self.mtp_enabled = switch.value

    def action_clear_chat(self) -> None:
        self.query_one("#chat_log", Log).clear()
        self.messages.clear()

    def action_switch_model(self) -> None:
        # Focus the model list for quick keyboard navigation
        self.query_one("#model_list", ListView).focus()


def run_tui() -> None:
    """Entry point for the Textual TUI."""
    app = NexTUI()
    app.run()
