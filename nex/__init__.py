"""
Nex — Multi-Model OptiQ Runner for Apple Silicon

A powerful local CLI + MCP server for the family of high-quality
MLX + OptiQ-4bit models (Qwen3/3.5/3.6, Gemma-4, Nemotron, MiniCPM, Nex, etc.).

All models load via the same `mlx_lm` interface. The app provides:
- Excellent chat with persistence and reasoning display
- Autonomous agent with safe sandboxed tools
- MCP server so other AIs can call these models
"""

__version__ = "0.2.0"   # Bumped for multi-model expansion

# Legacy constant kept for backward compatibility.
# New code should prefer `from nex.models import get_default_model`
DEFAULT_MODEL = "jedisct1/Nex-N2-mini-mlx-OptiQ-4bit"
