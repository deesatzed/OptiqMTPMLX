"""Core inference engine wrapping mlx-lm for the Nex model."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Optional, Tuple

from mlx_lm import load, stream_generate
from mlx_lm.sample_utils import make_sampler
from mlx_lm.tokenizer_utils import TokenizerWrapper

from rich.console import Console
from rich.status import Status

if TYPE_CHECKING:
    from .models import ModelProfile

console = Console()


@dataclass
class GenerationStats:
    prompt_tokens: int = 0
    generation_tokens: int = 0
    prompt_tps: float = 0.0
    generation_tps: float = 0.0
    peak_memory_gb: float = 0.0
    total_time: float = 0.0


@dataclass
class Engine:
    model_id: str = "jedisct1/Nex-N2-mini-mlx-OptiQ-4bit"
    draft_model_id: Optional[str] = None
    num_draft_tokens: int = 3
    _model: Any = field(default=None, repr=False)
    _tokenizer: Optional[TokenizerWrapper] = field(default=None, repr=False)
    _draft_model: Any = field(default=None, repr=False)
    _loaded: bool = False
    profile: Optional["ModelProfile"] = None   # populated on load if using registry

    def load(self) -> Tuple[Any, TokenizerWrapper]:
        """Lazy load the model and tokenizer. Idempotent. Shows nice spinner during load/download.
        If draft_model_id is set (for MTP/speculative decoding), it will be loaded too.
        """
        if self._loaded and self._model is not None and self._tokenizer is not None:
            return self._model, self._tokenizer

        t0 = time.time()
        with console.status(f"[bold cyan]Loading {self.model_id}[/bold cyan] (downloading on first run...)", spinner="dots"):
            model, tokenizer = load(self.model_id)
        self._model = model
        self._tokenizer = tokenizer

        if self.draft_model_id:
            with console.status(f"[bold cyan]Loading draft model for MTP: {self.draft_model_id}[/bold cyan]", spinner="dots"):
                draft_model, _ = load(self.draft_model_id)
            self._draft_model = draft_model
            console.print(f"[dim]MTP draft model loaded (num_draft_tokens={self.num_draft_tokens})[/dim]")

        self._loaded = True
        elapsed = time.time() - t0

        # Try to attach profile for smarter behavior
        try:
            from .models import get_profile
            self.profile = get_profile(self.model_id)
            if self.profile and self.profile.supports_mtp and not self.draft_model_id:
                # Auto-suggest or set if user didn't specify
                pass  # We let CLI decide whether to enable
        except Exception:
            self.profile = None

        console.print(f"[dim]Model ready in {elapsed:.1f}s[/dim]")
        if self.profile:
            mtp_str = " + MTP" if self._draft_model else ""
            console.print(f"[dim]Profile: {self.profile.name}{mtp_str} ({self.profile.family} · {self.profile.size_class})[/dim]")

            # Rough memory warning for larger models
            mem_map = {"tiny": 4, "small": 8, "medium": 18, "large": 30}
            est = mem_map.get(self.profile.size_class, 12)
            if est > 16:
                console.print(f"[yellow]Note: {self.profile.name} may use ~{est}GB+ unified memory. Close other apps if you see swapping.[/yellow]")
        return model, tokenizer

    def apply_chat_template(
        self,
        messages: List[Dict[str, str]],
        add_generation_prompt: bool = True,
    ) -> str:
        """Format messages using the model's chat template."""
        model, tokenizer = self.load()
        # Some wrappers expose it directly on the tokenizer
        if hasattr(tokenizer, "apply_chat_template"):
            return tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=add_generation_prompt,
                tokenize=False,
            )
        # Fallback: very rare for these models
        raise RuntimeError("Tokenizer does not support apply_chat_template")

    def stream_generate(
        self,
        prompt: str,
        *,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        top_p: float = 0.95,
        top_k: int = 0,
        seed: Optional[int] = None,
    ) -> Generator[Tuple[str, Optional[GenerationStats]], None, Optional[GenerationStats]]:
        """
        Stream tokens from the model.

        Yields (text_chunk, stats_or_None).
        On completion, the final yield has the aggregated stats (or return value).
        """
        model, tokenizer = self.load()

        start = time.time()
        prompt_tokens = 0
        gen_tokens = 0
        last_stats: Optional[GenerationStats] = None

        # Build sampler for this version of mlx-lm (sampling params go through sampler=)
        sampler = make_sampler(
            temp=temperature,
            top_p=top_p,
            top_k=top_k or 0,
        )

        # stream_generate accepts the already-templated prompt string
        gen_kwargs = {
            "max_tokens": max_tokens,
            "sampler": sampler,
        }
        if self._draft_model is not None:
            gen_kwargs["draft_model"] = self._draft_model
            gen_kwargs["num_draft_tokens"] = getattr(self, "num_draft_tokens", 3)

        for response in stream_generate(
            model,
            tokenizer,
            prompt,
            **gen_kwargs,
        ):
            text = response.text or ""
            gen_tokens += 1

            # Try to extract running stats if the response object provides them
            if hasattr(response, "prompt_tokens"):
                prompt_tokens = getattr(response, "prompt_tokens", prompt_tokens)
            if hasattr(response, "generation_tokens"):
                gen_tokens = getattr(response, "generation_tokens", gen_tokens)

            # Yield incremental text + partial stats
            yield text, None

        # After the loop we try to get authoritative numbers from the last response if available
        elapsed = time.time() - start

        # Best-effort stats extraction (different mlx_lm releases expose different fields on response)
        try:
            if hasattr(response, "prompt_tokens"):
                prompt_tokens = getattr(response, "prompt_tokens", prompt_tokens)
            if hasattr(response, "generation_tokens"):
                gen_tokens = getattr(response, "generation_tokens", gen_tokens)
        except Exception:
            pass

        # Compute rates. Prompt processing is very fast; we report what we observed.
        prompt_tps = prompt_tokens / max(elapsed * 0.05, 0.001)
        gen_tps = gen_tokens / max(elapsed, 0.001)

        # Memory (mlx exposes via mx)
        peak_mem = 0.0
        try:
            import mlx.core as mx

            if hasattr(mx, "get_peak_memory"):
                peak_mem = mx.get_peak_memory() / 1e9
            elif hasattr(mx.metal, "get_peak_memory"):
                peak_mem = mx.metal.get_peak_memory() / 1e9
            elif hasattr(mx.metal, "active_memory"):
                peak_mem = mx.metal.active_memory() / 1e9
        except Exception:
            pass

        stats = GenerationStats(
            prompt_tokens=prompt_tokens or 0,
            generation_tokens=gen_tokens,
            prompt_tps=round(prompt_tps, 2),
            generation_tps=round(gen_tps, 2),
            peak_memory_gb=round(peak_mem, 2),
            total_time=round(elapsed, 2),
        )
        last_stats = stats

        yield "", stats
        return stats

    def generate_once(
        self,
        prompt: str,
        *,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        top_p: float = 0.95,
        top_k: int = 0,
    ) -> Tuple[str, GenerationStats]:
        """Convenience non-streaming full generation. Returns (full_text, stats)."""
        full = []
        final_stats: Optional[GenerationStats] = None
        for chunk, stats in self.stream_generate(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
        ):
            if chunk:
                full.append(chunk)
            if stats is not None:
                final_stats = stats
        return "".join(full), (final_stats or GenerationStats())
