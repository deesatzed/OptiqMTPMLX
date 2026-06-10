"""Conversation session management (multi-turn chat with proper templating)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .engine import Engine, GenerationStats


@dataclass
class ChatSession:
    engine: Engine
    system_prompt: Optional[str] = None
    messages: List[Dict[str, str]] = field(default_factory=list)
    last_stats: Optional[GenerationStats] = None
    temperature: float = 0.7
    top_p: float = 0.95
    max_tokens: int = 1024

    def reset(self):
        self.messages.clear()
        self.last_stats = None

    def set_system(self, system: str):
        self.system_prompt = system.strip() or None
        # If conversation started, update or prepend system
        if self.messages and self.messages[0]["role"] == "system":
            if self.system_prompt:
                self.messages[0]["content"] = self.system_prompt
            else:
                self.messages.pop(0)
        elif self.system_prompt:
            self.messages.insert(0, {"role": "system", "content": self.system_prompt})

    def add_user(self, content: str):
        self.messages.append({"role": "user", "content": content.strip()})

    def add_assistant(self, content: str):
        self.messages.append({"role": "assistant", "content": content.strip()})

    def build_prompt(self) -> str:
        """Return the fully templated prompt string ready for generation."""
        msgs = list(self.messages)
        # Ensure system is present if we have one and it's not already first
        if self.system_prompt and (not msgs or msgs[0]["role"] != "system"):
            msgs = [{"role": "system", "content": self.system_prompt}] + msgs
        return self.engine.apply_chat_template(msgs, add_generation_prompt=True)

    def generate_stream(self):
        """Yield (chunk, stats) for the next assistant turn."""
        prompt = self.build_prompt()
        for chunk, stats in self.engine.stream_generate(
            prompt,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
        ):
            if stats is not None:
                self.last_stats = stats
            yield chunk, stats

    def generate_once(self) -> str:
        """Non-stream full response for the current turn. Appends to history."""
        prompt = self.build_prompt()
        text, stats = self.engine.generate_once(
            prompt,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
        )
        self.last_stats = stats
        self.add_assistant(text)
        return text
