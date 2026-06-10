# OptiqMTPMLX (Nex) — Grok in the Loop

**The only local AI runtime that gives you frontier Grok judgment at local OptiQ speed — with deterministic policy, continuous enforcement, and full auditable traces.**

Built iteratively with Grok. Fusing the best local MLX/OptiQ inference (this repo) with Cortex Sentinel safety (policy, PTY, enforcer, traces from gemOptq) and MCP-Cortex structured contracts.

> Most agents are either slow/expensive (always cloud) or dumber and untrustworthy (pure local).  
> This is the first stack that does both — and proves every decision.

**See [ARCHITECTURE_MERGE.md](./ARCHITECTURE_MERGE.md)** for the full fusion plan with gemOptq/Cortex Sentinel.  
**See [EXPANSION_PLAN.md](./EXPANSION_PLAN.md)** for the complete roadmap.

---

## The Real Problem (Needs First)

Developers and teams using autonomous agents (Claude Code, Cursor, Aider, custom MCP agents, etc.) face brutal trade-offs:

- **Cloud-only**: Insane cost, latency, and privacy leaks. Every token, every file read, every tool call goes to someone else's servers.
- **Pure local**: Fast and private, but the models are weaker on hard reasoning, tool use, and safety. Agents go rogue, touch secrets, propose bad deploys, or drift from intent — with zero audit trail.
- **No middle ground**: No way to get *Grok-level* judgment on the 5-10% of decisions that actually matter, while keeping 90%+ of the work blazing fast and local on Apple Silicon.

xAI built Grok to accelerate understanding the universe. Local agents should multiply human capability — not multiply risk or cost.

This is the missing piece: **Grok in the Loop**.

---

## What Only This App Can Do

No other local runner combines all of these at once:

- **Native MTP + multi-OptiQ models** (Nex-N2, Qwen3.5/3.6, Gemma-4, Nemotron...) on MLX for real 1.3-1.5× decode speedup and excellent quality/size on M-series.
- **Deterministic Sentinel policy + continuous enforcement + rollback** (ported from the mature gemOptq/Cortex Sentinel codebase) that blocks protected paths, secrets, external network, and production deploys *before* any model sees them.
- **MCP-Cortex capability contracts** so every tool the agent wants to call declares its effects upfront (read:secrets, write:workspace, network:external...).
- **Real Grok escalation**: Local OptiQ models handle the boring/fast parts. When policy or the local auditor says "review" (or risk is high), the *exact* structured context (intent + effects + trace + contract) is sent to real Grok (xAI API) for a high-quality JSON verdict + reasoning + safer alternative.
- **Unified auditable traces** that explicitly tag every decision as "local OptiQ" or "Grok escalated", with digests, latency, and full replay.
- **Production TUI + OpenAI/MCP servers** so you can supervise real external agents (Claude Code, Codex, Gemini) or use this as a drop-in local backend for Cursor/Continue/Aider — all under the same Grok + policy layer.
- **Built by Grok, for the xAI era** — meta, efficient, truth-seeking, and designed to multiply capability without creating new risks.

**Result**: 80-95% of work at laptop speed and <20-30W. The hard 5-10% gets real Grok. Every step is policy-enforced and replayable. This is what agentic AI should feel like in 2026.

---

## Grok in the Loop in Action

```bash
# The hybrid experience
GROK_IN_LOOP=true nex agent "Build a small FastAPI hello world in the sandbox, add tests, and verify it"

# Or supervise a real external agent (fusing full Cortex Sentinel)
# sentinel run --config sentinel.yaml -- claude .

# Drop-in server for any tool
nex serve --model qwen3.5-9b --enable-mtp
```

See the live demo script and video outline below.

---

## Current High-Leverage Features (All Implemented)

(From the original plan + Grok-in-the-Loop fusion session)

- Multi-model OptiQ registry with MTP speculative decoding
- Autonomous agent with safe sandbox tools + MCP-Cortex contracts
- Production Textual TUI (real multi-turn, live model/MTP switching, tool pane, Grok escalation visibility)
- Full OpenAI-compatible server (with tool_calls passthrough)
- MCP server + `nex_search_history`
- `nex models download | recommend | set-override`
- `nex self update | status | doctor` (uv-aware)
- Plugin system (`~/.nex/plugins/`)
- History RAG (optional `[rag]`)
- GrokEscalator + GrokAugmentedAuditor (local OptiQ + real xAI Grok)
- SentinelPolicy + ContinuousEnforcer (ported/adapted)
- Unified trace viewer (`nex trace replay`)
- Full fusion architecture documented with gemOptq/Cortex Sentinel + MCP-Cortex

See `ARCHITECTURE_MERGE.md` for exactly how the two repos combine.

---

## Quick Start (Tested on Fresh Clone)

```bash
# Fresh clone + modern uv path (recommended)
git clone https://github.com/deesatzed/OptiqMTPMLX.git
cd OptiqMTPMLX
uv venv .venv
uv pip install -e '.[server,tui,rag]'

# The hybrid demo (works with or without XAI_API_KEY)
python scripts/grok_in_loop_demo.py

# With real Grok escalation
GROK_IN_LOOP=true nex agent "Your goal here"

# Beautiful TUI
./run.sh tui

# OpenAI server (point Cursor/Aider at localhost:8000)
nex serve --model qwen3.5-9b --enable-mtp
```

Requires Apple Silicon Mac with Metal. First use of a model will download weights.

---

## Showpiece & Demo Assets

- **Polished landing page**: `docs/index.html` (open directly or `cd docs && python -m http.server 8080`)
- **Detailed showpiece brief**: `docs/showpiece/optiq-mtp-mlx.md`
- **Ready-to-record video script** (90-120s, designed to make Elon/xAI sit up): `docs/grok_in_loop_demo_video_script.md`

The video script and landing page are built around the *unique* "needs first" story above.

---

## Make Elon Proud — Why This Matters

- **Efficiency at the frontier**: Local OptiQ + MTP is the kind of brutal tokens-per-watt optimization Tesla/Dojo lives for. Grok is only called when it adds disproportionate value.
- **Auditable autonomy**: Real agents that can act, but with policy guardrails, rollback, and full traces (local decision vs Grok decision). This is the safety layer Optimus-scale autonomy will need.
- **xAI-native by construction**: Built with Grok. Uses Grok for the hard parts. Designed to multiply xAI's mission (understand the universe) by giving builders a local multiplier that doesn't sacrifice truth or capability.
- **Truth-seeking infrastructure**: Structured contracts, deterministic policy before LLM judgment, replayable evidence with digests. No vibes. No hidden cloud calls.
- **Anti-bloat, maximum truth**: uv-first, minimal deps, real code, no mocks. The kind of engineering velocity and honesty xAI stands for.

This isn't another local LLM wrapper. It's the reference implementation of what "Grok in the Loop" looks like for people actually shipping agentic systems.

---

## Next (Already in Motion)

The fusion with gemOptq/Cortex Sentinel is the secret sauce that makes the "only we can" claims real. See `ARCHITECTURE_MERGE.md` for the complete plan.

If you want to keep going:
- Deeper unified TUI with live Grok reasoning panel + full Sentinel approval queue
- Public trace gallery (redacted real sessions)
- Live efficiency dashboard (tokens/watt + thermal on M4)
- One-command "wrap any external agent under GrokSentinel"
- Actual end-to-end demo with Claude Code + Grok escalation + full replay

Let's keep building the thing that makes the future arrive faster and safer.

**Clone • `GROK_IN_LOOP=true nex agent "build something useful"` • Trace it • Tell the truth.**

Built with Grok. For the xAI era.

---

## Quick Start

```bash
cd /Volumes/WS4TB/nex-n2-mlx-run

source .venv/bin/activate
pip install -e .          # one time

# Interactive chat (auto-persisted)
nex

# One-shot
nex ask "Write a clean Python dataclass + Pydantic v2 validator example."

# Autonomous agent (can create/read/run code in ./sandbox)
nex agent "Create a small CLI tool that counts tokens in a file and write tests for it"

# List / resume sessions
nex sessions
nex resume
nex chat --session chat-20250610-...

# Start MCP server for other AIs
nex mcp
```

Convenience launcher (no need to remember activation) — now **uv-first**:

```bash
# Modern fast path (recommended)
uv venv .venv
uv pip install -e '.[tui]'
./run.sh chat --model qwen9b --mtp

# Or the classic way
python -m venv .venv && source .venv/bin/activate && pip install -e '.[tui]'
./run.sh tui
```

Self management & updates (uv-aware):

```bash
nex self status
nex self doctor
nex self update          # updates the app + deps (uses uv if present)
nex self update-deps
```

Modern TUI:

```bash
nex tui
nex chat --tui
``` (beautiful reactive interface with live model switching, MTP toggle, sidebar, etc.)
```

---

## Features

| Feature                  | Description |
|--------------------------|-------------|
| Chat                     | Multi-turn with full chat template support + streaming |
| **TUI (Textual)**        | Modern reactive terminal UI (`nex tui`) with live model switching, MTP toggle, sidebar, live stats |
| Persistence (default)    | Sessions saved in `./sessions/`. Auto-resumes latest unless `--no-persist` |
| Reasoning display        | `<think>` / scratchpad content rendered dim/italic when present |
| **MTP / Speculative**    | `--enable-mtp` for ~1.3-1.5× faster decode on supported models (e.g. Nex-MTP variant) |
| Agent mode               | Autonomous loop with 5 safe tools (see below) |
| JSONL logs               | Daily logs in `./logs/nex-YYYYMMDD.jsonl` |
| MCP server               | Full tool exposure for external AI clients (now with model + MTP params) |
| Multi-model + Registry   | `nex models list/info/add`, aliases (`qwen9b`, `gemma12b`, `nemotron`, `nex-mtp`...) |
| Sampling controls        | `--temperature`, `--top-p`, `--max-tokens`, `--system` everywhere |
| Self management          | `nex self update`, `nex self doctor`, `nex self status` (uv + pip aware) |
| Beautiful UX             | Rich panels, spinners during model load, clean stats + optional Textual TUI |

### In-chat commands

```
/help
/clear
/system You are a senior staff engineer...
/temp 0.2
/maxtokens 2048
/stats
/sessions
/resume [id]
/save backup.json
/load backup.json
/quit
```

---

## Agent Mode (`nex agent`)

The agent has access to a small set of **safe tools** that operate inside the protected `./sandbox/` directory:

- `list_dir(path)`
- `read_file(path)`
- `write_file(path, content)`
- `run_python(code)` — executes in a subprocess with 25s timeout
- `shell(command)` — only whitelisted safe commands (`ls`, `cat`, `head`, `grep`, etc.)

**Example goals:**

```bash
nex agent "Build a small FastAPI app with one endpoint and a test that hits it using httpx. Put everything in the sandbox."

nex agent "Analyze all .py files in the sandbox, find functions without type hints, and add them."
```

The agent uses a robust multi-format tool call parser (recommended XML style + JSON + ReAct) and will keep working until it produces a final answer or hits `--max-steps`.

---

## MCP Server — Let Other AIs Call This Model

This is the killer feature for using Nex as a **local specialist model** from Claude, Cursor, or any MCP-capable client.

### Running the server

```bash
source .venv/bin/activate
nex mcp

# or
python -m nex.mcp
# or
./run.sh mcp
```

The server runs over stdio (standard for MCP).

### Claude Desktop configuration

Add to your `claude_desktop_config.json` (usually in `~/Library/Application Support/Claude/` on macOS):

```json
{
  "mcpServers": {
    "nex-local": {
      "command": "/Volumes/WS4TB/nex-n2-mlx-run/.venv/bin/python",
      "args": ["-m", "nex.mcp"],
      "cwd": "/Volumes/WS4TB/nex-n2-mlx-run"
    }
  }
}
```

After restarting Claude Desktop, you should see tools like:

- `nex_ask`
- `nex_chat_turn`
- `nex_create_session` / `nex_list_sessions` / `nex_get_history`
- `nex_run_agent` (lets Claude drive the autonomous tool-using agent)

### Exposed MCP Tools (summary)

| Tool                | Purpose                                      | Stateful? |
|---------------------|----------------------------------------------|---------|
| `nex_ask`           | Fast one-shot generation                     | No      |
| `nex_chat_turn`     | Multi-turn in a named session                | Yes     |
| `nex_run_agent`     | Give the local model a goal + let it use tools | Yes (via session) |
| `nex_list_sessions` | See what persisted conversations exist       | -       |
| `nex_get_history`   | Retrieve full message history for a session  | -       |

All tools support `model`, `temperature`, `max_tokens`, etc.

### Example prompt you can give Claude

> "Use the nex-local MCP server. Create a clean, well-tested Python utility in the sandbox that walks a directory and produces a JSON report of file sizes and line counts. Use `nex_run_agent` or a combination of `nex_chat_turn` + `nex_ask`."

---

## Project Layout

```
nex-n2-mlx-run/
├── .venv/
├── nex/
│   ├── __init__.py
│   ├── cli.py          # All the commands
│   ├── engine.py       # Model loading + streaming (with nice spinner)
│   ├── session.py      # ChatSession + template application
│   ├── render.py       # Think-aware rich streaming
│   ├── persistence.py  # Sessions + daily JSONL logs
│   ├── tools.py        # Safe agent tools + multi-format parser
│   ├── agent.py        # Autonomous ReAct-style loop
│   └── mcp.py          # FastMCP server (the important one for other AIs)
├── sandbox/            # Agent workspace (safe)
├── sessions/           # Persisted JSON conversations
├── logs/               # Daily JSONL logs
├── run.sh              # Convenience launcher
├── pyproject.toml
└── README.md
```

---

## Development / Hacking

```bash
# Preferred (fast with uv)
uv venv .venv
uv pip install -e '.[server,tui,rag]'

# Or classic
source .venv/bin/activate
pip install -e '.[server,tui,rag]'

# Run
nex tui
nex serve
nex chat --model qwen3.5-9b --enable-mtp
```

### uv tool install (recommended for daily use)
```bash
uv tool install --from git+https://github.com/deesatzed/OptiqMTPMLX.git --python 3.12 nex-cli
# Then just `nex` anywhere
```

### Standalone / binary notes
- Use `uv build` for wheel.
- For single binary: `pip install pyinstaller && pyinstaller --onefile -n nex --add-data "nex:nex" -m nex.cli`
- Or use `uvx` / `uv tool` for isolated runs without full install.

The engine, tools, and persistence layers are designed to be reusable.

---

## OpenAI Server, TUI, Search & More

New high-leverage features (see EXPANSION_PLAN.md for full status):

- `nex serve [--port 8000] [--model qwen9b] [--enable-mtp]` — full OpenAI-compatible API (streaming + non-streaming, model + MTP passthrough). Works with Cursor, Continue.dev, Aider, custom agents, etc.
- `nex tui` — production Textual TUI with real multi-turn history (ChatSession + persistence), live model/MTP switching, think tag rendering, live stats.
- `nex search "your query"` — semantic search over your conversation history (install with `[rag]` extra).
- `nex models download <alias>` and `nex models recommend "coding tool use"` — one-command model discovery and management with memory estimates.
- `nex self update | update-deps | status | doctor` — uv-aware self management and health checks.
- Plugin system — easily add custom tools by dropping Python files in `~/.nex/plugins/` or `./plugins/` (example: `plugins/example_calculator.py`).

### Grok in the Loop (New High-Wow Feature)
Hybrid local + frontier reasoning:

```bash
GROK_IN_LOOP=true nex agent "Build a tiny FastAPI hello world and test it in the sandbox"
```

- Fast local OptiQ models (with MTP) do most of the work.
- Risky/ambiguous steps escalate to real Grok (xAI) with full structured context (intent + effects + trace).
- Full traces include local vs Grok decisions, latency, and reasoning.

See `scripts/grok_in_loop_demo.py`, `nex/grok_escalator.py`, and the MCP-Cortex adapter for structured tool effects.

Requires `XAI_API_KEY`. Falls back gracefully. This is the foundation for an auditable, efficient "Grok in the Loop" supervisor (see ARCHITECTURE_MERGE.md for how we are fusing with Cortex Sentinel concepts from gemOptq).

## Multi-Model Support (The Expansion)

The app has been expanded beyond a single model. It now supports the whole ecosystem of excellent **MLX + OptiQ-4bit** (and similar high-quality MLX) models.

### Why OptiQ models?
OptiQ is a sensitivity-aware mixed 4-bit quantization technique (from the mlx-optiq project). Almost all of them significantly outperform stock uniform 4-bit on reasoning, coding, and tool-use benchmarks while staying the same on-disk size.

Current strong families (all load the same way):
- **Qwen3 / Qwen3.5 / Qwen3.6** series (often the best for tool use + agentic work right now)
- **Gemma-4** (Google)
- **NVIDIA Nemotron** small models
- **MiniCPM5**, and various other well-converted models
- Special quants like the original `jedisct1/Nex-N2-mini-mlx-OptiQ-4bit`

### Using different models

```bash
# By alias (recommended)
nex chat --model qwen9b
nex chat --model gemma12b
nex agent "..." --model nemotron

# By partial name
nex ask "..." --model qwen3.5-4

# Full repo id (any mlx-lm compatible model works)
nex chat --model mlx-community/Qwen3.6-35B-A3B-OptiQ-4bit

# Discover models
nex models list
nex models list --family qwen --size small
nex models info qwen9b
```

### Adding / suggesting new models

The registry lives in `nex/models.py` (`KNOWN_MODELS`).

To add a new great OptiQ (or other high-quality MLX) model:

1. Add a `ModelProfile(...)` entry with good `recommended_*` values and `strengths`.
2. Add useful aliases.
3. (Optional) Provide a custom `agent_tool_instructions` if the model is picky about tool format.
4. Test it with `nex chat --model <new-one>` and `nex agent`.

PRs that add well-tested OptiQ models (especially strong tool-use / coding ones) are very welcome.

### Environment variable for default model

```bash
export NEX_DEFAULT_MODEL=mlx-community/Qwen3.5-9B-OptiQ-4bit
```

This is the cleanest way to switch your daily driver.

### MCP + multi-model

All MCP tools accept a `model` parameter. A Claude (or other MCP client) can freely switch between a fast tiny model for simple tasks and a stronger 9B/27B model for hard agent work — all on the same local machine.

Example tool call from another AI:
```
nex_chat_turn( session_id=..., prompt=..., model="qwen3.5-9b" )
```

---

## Model (Original)

- The app was originally built around `jedisct1/Nex-N2-mini-mlx-OptiQ-4bit`
- Still one of the best small "agentic" models in the OptiQ lineup
- All other models in the registry use the exact same loading and inference path

---

## License

The CLI wrapper code is MIT.  
The model itself follows the license on its Hugging Face page.

Enjoy your fast, private, agentic local model!
