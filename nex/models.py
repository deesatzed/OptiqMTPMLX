"""
Model Registry for MLX + OptiQ (and similar high-quality MLX quants).

This is the foundation for expanding the app beyond a single model
to the whole family of excellent OptiQ-4bit (and other mlx-lm) models:

- Qwen3 / Qwen3.5 / Qwen3.6 family (currently the strongest small/medium for tool use + coding)
- Gemma-4 family
- NVIDIA Nemotron small models
- MiniCPM, Phi, and other well-converted models
- Custom / jedisct1 special quants (like the original Nex-N2)

All these models load identically via `mlx_lm.load("org/model-name-OptiQ-4bit")`.
The differences are in:
- Reasoning/tool-following quality
- Optimal sampling parameters
- Chat template behavior
- Memory footprint and speed on Apple Silicon
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from . import DEFAULT_MODEL


@dataclass
class ModelProfile:
    repo_id: str
    name: str                          # Short friendly name
    family: str                        # qwen, gemma, nemotron, minicpm, nex, other
    size_class: str                    # tiny, small, medium, large
    params: str                        # "4B", "9B", "27B-A3B", etc.
    quant: str = "OptiQ-4bit"

    # Recommended runtime defaults
    recommended_temperature: float = 0.6
    recommended_max_tokens: int = 1536
    recommended_top_p: float = 0.95

    # Strengths (used for filtering and smart defaults)
    strengths: List[str] = field(default_factory=list)   # e.g. ["coding", "tool_use", "reasoning", "speed", "general"]

    # Notes for the user
    notes: str = ""

    # Whether this model tends to emit <think> / reasoning traces
    emits_thinking: bool = True

    # Extra system prompt guidance for agent/tool mode (overrides the generic one when present)
    agent_tool_instructions: Optional[str] = None

    # Aliases the user can type on the CLI (fuzzy + exact match supported)
    aliases: List[str] = field(default_factory=list)

    # MTP / Speculative Decoding (Multi-Token Prediction) support
    supports_mtp: bool = False
    mtp_repo_id: Optional[str] = None  # e.g. the -MTP variant repo for draft_model
    recommended_num_draft_tokens: int = 3


# =============================================================================
# Curated high-quality OptiQ (and close relatives) registry
# =============================================================================
# These are all confirmed to work with mlx_lm as of mid-2026.
# Prioritized by real-world usefulness on Apple Silicon (tool use + coding + speed).

KNOWN_MODELS: Dict[str, ModelProfile] = {
    # --- Original / Special ---
    "nex-n2-mini": ModelProfile(
        repo_id="jedisct1/Nex-N2-mini-mlx-OptiQ-4bit",
        name="Nex-N2-Mini",
        family="nex",
        size_class="small",
        params="~2-3B class",
        recommended_temperature=0.5,
        recommended_max_tokens=1536,
        strengths=["coding", "tool_use", "agentic", "reasoning"],
        notes="Original model this app was built around. Strong at autonomous task execution and tool use.",
        aliases=["nex", "n2", "nex-mini", "original"],
        supports_mtp=True,
        mtp_repo_id="jedisct1/Nex-N2-mini-mlx-OptiQ-4bit-MTP",
        recommended_num_draft_tokens=3,
    ),
    "nex-n2-mini-mtp": ModelProfile(
        repo_id="jedisct1/Nex-N2-mini-mlx-OptiQ-4bit-MTP",
        name="Nex-N2-Mini-MTP",
        family="nex",
        size_class="small",
        params="~2-3B class + MTP",
        recommended_temperature=0.5,
        recommended_max_tokens=1536,
        strengths=["coding", "tool_use", "agentic", "reasoning", "speed"],
        notes="Nex-N2-Mini with bundled Multi-Token Prediction (MTP) head for speculative decoding (~1.3-1.5x speedup). Use as draft_model on the base, or load directly.",
        aliases=["nex-mtp", "n2-mtp", "nex-mini-mtp"],
        supports_mtp=True,
        mtp_repo_id="jedisct1/Nex-N2-mini-mlx-OptiQ-4bit-MTP",
        recommended_num_draft_tokens=3,
    ),

    # --- Qwen3.5 / Qwen3.6 family (currently the best overall for most users) ---
    "qwen3.5-0.8b": ModelProfile(
        repo_id="mlx-community/Qwen3.5-0.8B-OptiQ-4bit",
        name="Qwen3.5-0.8B-OptiQ",
        family="qwen",
        size_class="tiny",
        params="0.8B",
        recommended_temperature=0.6,
        recommended_max_tokens=2048,
        strengths=["speed", "general", "coding"],
        notes="Extremely fast tiny model. Surprisingly capable for its size.",
        aliases=["qwen08", "qwen-0.8", "qwen-tiny"],
    ),
    "qwen3.5-4b": ModelProfile(
        repo_id="mlx-community/Qwen3.5-4B-OptiQ-4bit",
        name="Qwen3.5-4B-OptiQ",
        family="qwen",
        size_class="small",
        params="4B",
        recommended_temperature=0.55,
        recommended_max_tokens=2048,
        strengths=["coding", "tool_use", "reasoning", "speed"],
        notes="Excellent sweet spot. Very strong at tool calling and structured output among small models.",
        aliases=["qwen4b", "qwen-4", "qwen3.5-4"],
    ),
    "qwen3.5-9b": ModelProfile(
        repo_id="mlx-community/Qwen3.5-9B-OptiQ-4bit",
        name="Qwen3.5-9B-OptiQ",
        family="qwen",
        size_class="small",
        params="9B",
        recommended_temperature=0.6,
        recommended_max_tokens=2048,
        strengths=["coding", "tool_use", "reasoning"],
        notes="One of the best price/performance models in the OptiQ lineup for agentic work.",
        aliases=["qwen9b", "qwen-9"],
    ),
    "qwen3.5-27b": ModelProfile(
        repo_id="mlx-community/Qwen3.5-27B-OptiQ-4bit",
        name="Qwen3.5-27B-OptiQ",
        family="qwen",
        size_class="medium",
        params="27B",
        recommended_temperature=0.65,
        recommended_max_tokens=3072,
        strengths=["coding", "reasoning", "tool_use"],
        notes="Big step up in capability. Needs more unified memory (~18-24GB+ recommended for comfortable use).",
        aliases=["qwen27b", "qwen-27"],
    ),
    "qwen3.6-27b": ModelProfile(
        repo_id="mlx-community/Qwen3.6-27B-OptiQ-4bit",
        name="Qwen3.6-27B-OptiQ",
        family="qwen",
        size_class="medium",
        params="27B",
        recommended_temperature=0.6,
        recommended_max_tokens=3072,
        strengths=["coding", "tool_use", "reasoning"],
        notes="Qwen3.6 series improvements over 3.5. Excellent for complex agent loops.",
        aliases=["qwen3.6-27"],
    ),
    "qwen3.6-35b-a3b": ModelProfile(
        repo_id="mlx-community/Qwen3.6-35B-A3B-OptiQ-4bit",
        name="Qwen3.6-35B-A3B-OptiQ",
        family="qwen",
        size_class="medium",
        params="35B-A3B (MoE)",
        recommended_temperature=0.55,
        recommended_max_tokens=4096,
        strengths=["coding", "tool_use", "reasoning"],
        notes="Mixture-of-Experts. Very strong capability with moderate active parameters. Great for long agent sessions.",
        aliases=["qwen35b", "qwen-moe", "qwen3.6-moe"],
    ),

    # --- Gemma-4 family ---
    "gemma-4-12b": ModelProfile(
        repo_id="mlx-community/gemma-4-12B-it-OptiQ-4bit",
        name="Gemma-4-12B-OptiQ",
        family="gemma",
        size_class="small",
        params="12B",
        recommended_temperature=0.7,
        recommended_max_tokens=2048,
        strengths=["general", "reasoning", "coding"],
        notes="Google's Gemma-4 in high-quality OptiQ. Sometimes more 'creative' than Qwen family.",
        aliases=["gemma12b", "gemma-12"],
    ),

    # --- NVIDIA Nemotron ---
    "nemotron-nano-4b": ModelProfile(
        repo_id="mlx-community/NVIDIA-Nemotron-3-Nano-4B-OptiQ-4bit",
        name="Nemotron-3-Nano-4B-OptiQ",
        family="nemotron",
        size_class="small",
        params="4B",
        recommended_temperature=0.6,
        recommended_max_tokens=1536,
        strengths=["coding", "reasoning"],
        notes="NVIDIA's small model. Often very good at following instructions and structured output.",
        aliases=["nemotron", "nemotron-4b", "nvidia-nano"],
    ),

    # --- Other notable OptiQ ---
    "minicpm5-1b": ModelProfile(
        repo_id="mlx-community/MiniCPM5-1B-OptiQ-4bit",
        name="MiniCPM5-1B-OptiQ",
        family="minicpm",
        size_class="tiny",
        params="1B",
        recommended_temperature=0.65,
        recommended_max_tokens=1536,
        strengths=["speed", "general"],
        notes="Hybrid reasoning model from OpenBMB. Has an `enable_thinking` mode in some templates.",
        aliases=["minicpm", "minicpm1b"],
    ),
}

# Reverse lookup: repo_id -> key
REPO_TO_KEY: Dict[str, str] = {p.repo_id: key for key, p in KNOWN_MODELS.items()}


def get_profile(model: str) -> ModelProfile:
    """
    Resolve a model string (repo id, key, or alias) to a ModelProfile.
    Falls back to a generic profile if unknown.
    """
    model = model.strip()

    # Exact key match
    if model in KNOWN_MODELS:
        return KNOWN_MODELS[model]

    # Alias match (case insensitive)
    model_lower = model.lower()
    for key, profile in KNOWN_MODELS.items():
        if model_lower in [a.lower() for a in profile.aliases]:
            return profile
        if model_lower == profile.name.lower():
            return profile

    # Repo id exact match
    if model in REPO_TO_KEY:
        return KNOWN_MODELS[REPO_TO_KEY[model]]

    # Partial / fuzzy match on key or name
    for key, profile in KNOWN_MODELS.items():
        if model_lower in key.lower() or model_lower in profile.name.lower():
            return profile

    # Unknown model — return a sensible generic profile
    return ModelProfile(
        repo_id=model,
        name=model.split("/")[-1],
        family="other",
        size_class="unknown",
        params="?",
        notes="Custom or less common model. Using generic defaults.",
        strengths=["general"],
    )


def list_profiles(
    family: Optional[str] = None,
    size_class: Optional[str] = None,
    min_strength: Optional[str] = None,
) -> List[ModelProfile]:
    """Return filtered list of known profiles."""
    results = list(KNOWN_MODELS.values())

    if family:
        results = [p for p in results if p.family.lower() == family.lower()]
    if size_class:
        results = [p for p in results if p.size_class.lower() == size_class.lower()]
    if min_strength:
        results = [p for p in results if min_strength.lower() in [s.lower() for s in p.strengths]]

    return results


def get_default_model() -> str:
    """Allow override via env var > config file > built-in default."""
    import os
    from .config import get_default_model as _cfg_default

    env = os.environ.get("NEX_DEFAULT_MODEL")
    if env:
        return env
    cfg = _cfg_default()
    if cfg:
        return cfg
    return DEFAULT_MODEL


def suggest_similar(current_repo: str, limit: int = 4) -> List[ModelProfile]:
    """Suggest other good models in the same family or size class."""
    current = get_profile(current_repo)
    candidates = [
        p for p in KNOWN_MODELS.values()
        if p.repo_id != current.repo_id
    ]

    # Prefer same family
    same_family = [p for p in candidates if p.family == current.family]
    if same_family:
        candidates = same_family + [p for p in candidates if p not in same_family]

    # Prefer similar size
    candidates.sort(key=lambda p: (p.family != current.family, p.size_class != current.size_class))
    return candidates[:limit]
