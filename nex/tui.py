"""
Production-grade Textual TUI for Nex.

Features implemented in this version:
- Real multi-turn using ChatSession + persistence
- Markdown rendering + basic thinking awareness
- Live model switching from registry (with MTP variants)
- MTP toggle that reloads engine
- Live stats
- Keyboard navigation

Run with:
    nex tui
    ./run.sh tui
"""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import (
    Footer,
    Header,
    Input,
    Label,
    ListView,
    ListItem,
    Markdown,
    Static,
    Switch,
)

from .engine import Engine
from .models import get_default_model, get_profile, list_profiles
from .persistence import (
    SessionRecord,
    load_session,
    new_session_id,
    save_session,
)
from .session import ChatSession as CoreChatSession
from .theme import get_color


class NexTUI(App):
    """SOTA Textual experience for the OptiQ multi-model runner."""

    CSS = """
    Screen { background: $surface; }
    #sidebar { width: 30; background: $panel; border-right: thick $primary; }
    #chat_log { height: 1fr; border: round $accent; padding: 1; overflow-y: auto; }
    #input { dock: bottom; margin: 1 0; }
    #stats { height: auto; background: $boost; border: round $secondary; padding: 0 1; }
    .title { padding: 0 1; text-style: bold; }
    .active { background: $accent; color: $text; }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+m", "focus_models", "Models"),
        Binding("ctrl+t", "toggle_mtp", "Toggle MTP"),
        Binding("ctrl+l", "clear", "Clear"),
        Binding("ctrl+n", "new_session", "New Session"),
    ]

    current_model: reactive[str] = reactive(get_default_model())
    mtp_enabled: reactive[bool] = reactive(False)
    stats_text: reactive[str] = reactive("Ready")

    def __init__(self):
        super().__init__()
        self.engine: Engine | None = None
        self.chat_session: CoreChatSession | None = None
        self.record: SessionRecord | None = None
        self.sid = new_session_id("tui")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal():
            with Vertical(id="sidebar"):
                yield Label("Models", classes="title")
                yield ListView(id="model_list")
                yield Label("MTP", classes="title")
                yield Switch(value=self.mtp_enabled, id="mtp_switch")

            with Vertical():
                yield Markdown(id="chat_log")
                yield Input(placeholder="Type your message and press Enter...", id="input")
                yield Static(self.stats_text, id="stats")

        yield Footer()

    def on_mount(self) -> None:
        self.title = "Nex • Multi-Model OptiQ + MTP"
        self.sub_title = "Beautiful local AI on Apple Silicon"
        self._load_models()
        self._init_session()
        self._load_engine()
        self.query_one("#input", Input).focus()
        self._refresh_view()

    # --- Models & Engine ---

    def _load_models(self) -> None:
        lv = self.query_one("#model_list", ListView)
        lv.clear()
        for p in list_profiles():
            item = ListItem(Label(f"{p.name}"), name=p.repo_id)
            if p.repo_id == self.current_model:
                item.add_class("active")
            lv.append(item)

    def _load_engine(self) -> None:
        draft = None
        if self.mtp_enabled:
            prof = get_profile(self.current_model)
            if prof.supports_mtp and prof.mtp_repo_id:
                draft = prof.mtp_repo_id

        self.engine = Engine(
            model_id=self.current_model,
            draft_model_id=draft,
            num_draft_tokens=3,
        )
        self.engine.load()

        prof = get_profile(self.current_model)
        mtp = " + MTP" if self.mtp_enabled else ""
        self.stats_text = f"{prof.name}{mtp}"
        self.query_one("#stats", Static).update(self.stats_text)

        # Re-attach engine to chat session
        if self.chat_session:
            self.chat_session.engine = self.engine

    def watch_mtp_enabled(self, value: bool) -> None:
        self._load_engine()

    def on_switch_changed(self, event: Switch.Changed) -> None:
        if event.switch.id == "mtp_switch":
            self.mtp_enabled = event.value

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id == "model_list" and event.item and event.item.name:
            new_model = str(event.item.name)
            if new_model != self.current_model:
                self.current_model = new_model
                self._load_models()
                self._load_engine()
                self.query_one("#chat_log", Markdown).update(
                    (self.query_one("#chat_log", Markdown).renderable or "") + 
                    f"\n\n[dim]→ Switched to {get_profile(new_model).name}[/dim]"
                )

    # --- Session Management ---

    def _init_session(self) -> None:
        self.record = load_session(self.sid) or SessionRecord(session_id=self.sid)
        self.chat_session = CoreChatSession(engine=self.engine or Engine(self.current_model))
        if self.record.messages:
            self.chat_session.messages = list(self.record.messages)
            if self.record.system_prompt:
                self.chat_session.system_prompt = self.record.system_prompt

    def _refresh_view(self) -> None:
        log = self.query_one("#chat_log", Markdown)
        content_lines = []
        for msg in (self.chat_session.messages if self.chat_session else []):
            role = "**You:**" if msg["role"] == "user" else "**Nex:**"
            text = msg["content"].strip()
            # Simple think tag handling for nicer display in Markdown
            if "<think>" in text and "</think>" in text:
                before, rest = text.split("<think>", 1)
                think_content, after = rest.split("</think>", 1)
                text = f"{before}\n\n> **Thinking:**\n> {think_content.strip()}\n\n{after}"
            content_lines.append(f"{role} {text}")
        log.update("\n\n".join(content_lines) or "*Start typing below...*")

    def _persist(self) -> None:
        if self.record and self.chat_session:
            self.record.messages = self.chat_session.messages
            save_session(self.record)

    # --- Chat ---

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text or not self.engine or not self.chat_session:
            return

        event.input.value = ""

        self.chat_session.add_user(text)
        self._refresh_view()
        self._persist()

        self.run_worker(self._generate(text), exclusive=True)

    async def _generate(self, user_text: str) -> None:
        log = self.query_one("#chat_log", Markdown)

        try:
            prompt = self.chat_session.build_prompt()
            full_response: list[str] = []

            for chunk, stats in self.engine.stream_generate(
                prompt,
                max_tokens=self.chat_session.max_tokens,
                temperature=self.chat_session.temperature,
                top_p=self.chat_session.top_p,
            ):
                if chunk:
                    full_response.append(chunk)
                if stats:
                    self.stats_text = (
                        f"{stats.generation_tokens} tok @ {stats.generation_tps:.1f} t/s  "
                        f"peak {stats.peak_memory_gb:.1f} GB"
                    )
                    if self.mtp_enabled:
                        self.stats_text += " [MTP]"
                    self.query_one("#stats", Static).update(self.stats_text)

            assistant_text = "".join(full_response).strip()
            self.chat_session.add_assistant(assistant_text)
            self._refresh_view()
            self._persist()

        except Exception as e:
            log.update(f"**Error during generation:** {e}")

    # --- Actions ---

    def action_toggle_mtp(self) -> None:
        sw = self.query_one("#mtp_switch", Switch)
        sw.value = not sw.value
        self.mtp_enabled = sw.value

    def action_focus_models(self) -> None:
        self.query_one("#model_list", ListView).focus()

    def action_clear(self) -> None:
        if self.chat_session:
            self.chat_session.reset()
        self.query_one("#chat_log", Markdown).update("*Conversation cleared*")
        self._persist()

    def action_new_session(self) -> None:
        self.sid = new_session_id("tui")
        self.record = SessionRecord(session_id=self.sid)
        self.chat_session = CoreChatSession(engine=self.engine or Engine(self.current_model))
        self.query_one("#chat_log", Markdown).update("*New session started*")
        self._persist()


def run_tui() -> None:
    NexTUI().run()