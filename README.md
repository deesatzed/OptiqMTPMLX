# OptiqMTPMLX (Nex) — Grok in the Loop

**Grokkasclate — the only local AI runtime that gives you frontier Grok judgment at local OptiQ speed — with deterministic policy, continuous enforcement, and full auditable traces.** (play on "grok" + "escalate")

Built iteratively with Grok. Fusing the best local MLX/OptiQ inference (this repo) with Cortex Sentinel safety (policy, PTY, enforcer, traces from gemOptq) and MCP-Cortex structured contracts.

> Most agents are either slow/expensive (always cloud) or dumber and untrustworthy (pure local).  
> This is the first stack that does both — and proves every decision.

**See [ARCHITECTURE_MERGE.md](./ARCHITECTURE_MERGE.md)** for the full fusion plan with gemOptq/Cortex Sentinel.  
**See [EXPANSION_PLAN.md](./EXPANSION_PLAN.md)** for the complete roadmap.

---

## The Real Problem (Needs First — What No One Else Solves Well)

Developers shipping with agents (Claude Code, Cursor, Aider, custom tools, or their own local models) have these painful, unmet needs today:

1. **Speed + Privacy + Cost Control Without Sacrificing Capability**  
   Cloud agents are too slow/expensive/leaky for daily work. Pure local agents are fast and private but lack the reasoning depth for complex tasks, creative leaps, or safe decision-making on ambiguous/high-stakes actions.

2. **Safety That Actually Works Without Killing Productivity**  
   Agents are powerful precisely because they can read/write/run freely — but that makes them dangerous. Current tools have weak, model-dependent "safety" (easily jailbroken or ignored). No deterministic policy, no automatic rollback, no way to supervise the *real* agents you already use every day (Claude Code, Cursor, etc.).

3. **Frontier Intelligence Only When It Matters — With Proof**  
   You don't want (or can't afford) to send every token to Grok/Claude. You want local models for the 80-95% routine work, but real Grok-quality judgment + reasoning for the risky/ambiguous/creative 5-20%. And you need an audit trail that clearly shows *why* a decision was local vs escalated, what context was used, and what the outcome was.

4. **Auditability & Replay for Real Work (Not Toy Logs)**  
   When an agent does something surprising (or you need to debug, review with a team, or prepare for higher-stakes use), you need structured, replayable evidence — not raw terminal logs. This includes policy decisions, tool effects declared *before* execution, and the exact input/output when Grok was consulted.

5. **Use the Agents I Already Love — But Better**  
   People don't want to abandon Claude Code or Cursor. They want to wrap/supervise them with better policy, Grok oversight, efficiency, and traces — without changing their daily workflow.

6. **Efficiency at the Hardware Level (Apple Silicon Reality)**  
   On M-series Macs, you can do dramatically better than cloud or generic local runners if you use advanced quantization (OptiQ) + speculative decoding (MTP). But no one exposes this in a full agent supervision stack with hybrid escalation and safety.

These are not nice-to-haves. They are the blockers preventing teams from trusting agents for real, high-volume, high-stakes work.

**Only this fused stack (Nex OptiQ inference + Sentinel policy/enforcement/traces + MCP-Cortex contracts + real Grok escalation + PTY supervision of external agents) can address all of them at once.**

This is Grokkasclate: the missing control layer for the agentic era.

---

## Grokkasclate Explained (Like You're a College Freshman)

Imagine you're a college freshman who just started coding. You have a super smart AI buddy (like Claude or Cursor) that helps you write code for class projects or your side hustle app. You type what you want in plain English ("make a website that tracks my coffee intake"), and it spits out code, edits files, and even runs commands.

**The problem:** That AI buddy is like a really smart but super reckless roommate. It can do amazing things fast, but it might:
- Accidentally delete important files.
- Write your secret passwords into a public file.
- Try to "deploy" something to the internet without asking.
- Just do weird stuff because it "thought" it was helping.

Right now, most AI coding tools are either:
- Always in the cloud (slow, costs money every time you use it, and your code is sent to some company).
- Or running on your laptop but with no real "adult supervision" — the AI can do whatever it wants to your computer.

**What we built (Grokkasclate):** Think of it as a smart, trustworthy "RA" (Resident Advisor) or babysitter that sits between you and your AI coding buddy.

It lets you keep using the exact same AI tools you already love (Claude Code, Cursor, Codex, Aider — whatever your favorite is). You don't have to switch apps or learn new habits.

Here's what it actually does in normal-person terms:
- It **watches in real time** what the AI is doing to your files and computer (using real low-level computer magic, not just trusting what the AI says).
- It has **real rules** (not "the AI promised it was safe"). If the AI tries to touch secret files, production stuff, or do something sketchy, it can automatically stop it or ask you first.
- For the really tricky decisions, it can **call in the big brain** — a powerful model from xAI called Grok — to get a second opinion with full context.
- It has a nice screen (the TUI) where risky actions show up in a queue. You can approve, block, or override them easily, like approving app permissions on your phone.
- It keeps a full **video-replay style record** of everything that happened (what the local fast AI did, when it asked Grok, what you approved). You can export a clean, redacted version to show your team, professor, or future employer.
- It can **wrap your existing tools** with one command so that when you type `claude .` or `codex .` like you always do, it's now running under this safety net.

It uses a fast, efficient version of AI that runs directly on your Mac laptop (using special Apple Silicon tricks for speed and battery life). Most of the work stays private and instant on your machine. Only when something actually looks risky does it reach out to the smarter (but slower/more expensive) Grok.

**Why a "vibe coder" or any software engineer would want it:**

If you're a vibe coder (you casually prompt AI, iterate fast, "vibe" with the tool to build stuff without super formal plans):
- You get to keep moving at the speed of thought with your favorite AI.
- But you stop having that background anxiety of "did it just mess up my repo?"
- Your projects feel more "real" and shippable because there's actual guardrails.
- You can show off clean audit logs when you apply for internships or work on group projects.

If you're any SWE (even a serious one):
- You can use the exact powerful agents your team or you already use every day (no forcing everyone to switch to a new "safe" IDE).
- Real safety that actually watches what happens on disk, not just model-generated warnings that the AI can ignore.
- When you're working on something important (client code, open source, personal projects with real data), you have proof of what happened and why.
- It stays fast and cheap because the heavy lifting is local and efficient. Grok only gets called for the actual hard/risky moments.
- For teams: everyone can have the same safety net without changing how they work.

**Why it's novel (why no one else has this yet):**

Most "AI safety" for coding is either:
- The model itself saying "I'll be careful" (easy to trick or forget).
- Or tools that make you use *their* special agent only (you lose the muscle memory and power of the one you already like).
- Or cloud-only things that are slow and send all your code away.

Grokkasclate is different because:
- It **wraps the agents you already use** (via a clever terminal trick called PTY) so your daily workflow stays exactly the same.
- It uses **real computer-level watching** of file changes (a "ContinuousEnforcer" that snapshots and diffs what actually changed on disk) combined with smart policy rules. This is deterministic safety, not probabilistic "the model feels good about this."
- It does the **smart hybrid thing**: super fast, private, battery-friendly local model for 95% of the boring/safe work + escalates to real Grok (with rich context about exactly what the agent was trying to do) only for the 5% that matters.
- It gives you **visible human control + full replayable proof**. You see the queue, you decide, and later you (or anyone) can replay the entire story with "this is exactly what the local AI decided, this is when Grok was asked, this is what you approved."
- Everything is designed to be **reproducible and auditable** from a fresh clone — no magic, no mocks.

In short: It's the first thing that lets normal coders (vibe or pro) use the AI tools they already love at full power, while actually having grown-up supervision, real records, and smart escalation to a frontier model only when the local one shouldn't be trusted alone.

Think of it as training wheels that actually work, for the wild west of AI coding agents — but the training wheels are invisible most of the time and only kick in when you actually need them.

---

## Screenshots & Visual Demos (Placeholders)

<!-- TODO: Replace these placeholders with real screenshots or asciinema casts once recorded. Suggested shots below. -->

### Key Visuals to Capture

**1. Live PTY + Real Enforcer Interception**
- Run the showpiece or `nex supervise` with a risky agent.
- Show the terminal where the "agent" tries to write .env and gets blocked live.
- Caption: "Real filesystem observation catching a production secret leak in real time (no text scraping)."

**2. TUI Approvals Queue**
- The richer TUI with pending approvals pane.
- Show a/b/o key hints and Grok verdict.
- Caption: "Human-in-the-loop approvals with full context — visible in the same beautiful TUI you chat in."

**3. Oversight & Efficiency Report**
- The colored panel at end of agent/supervise run showing local tokens, t/s, grok escalations, blocks, wall time.
- Caption: "Measurable proof: 95%+ local OptiQ speed, real policy decisions, Grok only when it matters."

**4. Redacted Trace Gallery**
- Output of `nex trace-gallery --redact`.
- Caption: "Shareable, auditable artifact for teams, compliance, or demos. Everything replayable."

**5. One-Command Permanent Wrap (`--install`)**
- The output of `nex supervise --install`.
- Caption: "One command to make your existing daily drivers (claude, codex, etc.) always Grokkasclate-protected."

(We currently describe these since no real images are committed yet — see EXPANSION_PLAN.md history.)

---

## Asciinema / Terminal Recording Support

For lightweight, embeddable demos (no heavy video files):

1. Install asciinema: `brew install asciinema` (or equivalent for your OS).
2. Record the showpiece cleanly:
   ```bash
   asciinema rec --command 'python scripts/grokkasclate_showpiece.py' grokkasclate-demo.cast
   ```
3. Upload the .cast to https://asciinema.org (free hosting + embed code) or self-host.
4. Embed in README or landing page like:
   ```markdown
   [![asciicast](https://asciinema.org/a/XXXXX.svg)](https://asciinema.org/a/XXXXX)
   ```

The `grokkasclate_showpiece.py` now prints recording instructions at the end.

This gives beautiful terminal "screenshots" that play back the exact PTY interception, queue, reports, etc.

---

This is Grokkasclate: the missing control layer for the agentic era.

---

## What Only This App Can Do (Unmet Needs → Unique Capabilities)

No other tool addresses the full set of needs above because no other tool has this combination:

- **Local OptiQ + MTP at native speed** on Apple Silicon (multi-model registry of the best 4-bit mixed-precision quants + speculative decoding). This directly solves the efficiency/privacy/cost need that cloud agents fail and generic local runners only partially meet.
- **Deterministic policy + continuous enforcement + rollback** (from the gemOptq/Cortex Sentinel layer). Hard blocks on secrets, protected paths, external network, production deploys — with automatic rollback. This is the safety-without-friction need that model "safety" features in Claude/Cursor never reliably solve.
- **MCP-Cortex capability contracts** for tools. Effects are declared *before* execution and fed into policy/Grok. This is the structured tool-use safety need that almost nothing provides today.
- **Real Grok escalation with rich context**. Local models for the fast 80-95%. When policy or local auditor flags risk/ambiguity, the *exact* intent + effects + trace + contract goes to real Grok for a structured verdict + safer alternative. This uniquely solves the "I want Grok quality without the cloud tax" need.
- **Unified traces that distinguish local vs Grok decisions**. Every policy action, every tool effect, every escalation, every human override — with stable digests and full replay. This is the auditability need for real work, compliance, debugging, or future high-stakes autonomy (Optimus-scale, etc.).
- **First-class supervision of the external agents you already use** (Claude Code, Cursor/Codex, Gemini, Aider, etc.) via PTY runner + trust prompt injection + approval queue (borrowed and extended from gemOptq's real-agent harness). Plus the same layer for your own local Nex agents. This is the "use what I already love, but make it safe and smarter" need that pure new local tools ignore.
- **Grok-native by construction** (the whole project, including the escalation logic and fusion plan, was built iteratively with Grok). This is the meta need for tools that actually advance xAI's mission rather than just wrapping models.

**Result**: You get the speed and privacy of local + the judgment of Grok + the safety and auditability of a real supervision layer — for both your local work *and* the agents you already ship with. No other stack delivers this full set.

---

## Grok in the Loop in Action (Addressing the Real Needs)

```bash
# Use your own local agent with Grok escalation + full policy
GROK_IN_LOOP=true nex agent "Build a small FastAPI hello world in the sandbox, add tests, and verify it"

# Or wrap the agents you already use every day (the Extra Big Wow)
nex supervise claude .                    # or grok-claude .
grok-codex .                              # Cursor-style Codex under the same layer
nex supervise codex --grok-in-loop
nex supervise --install                   # ONE command to make claude/codex ALWAYS supervised (aliases + hooks)

# Real continuous enforcement + redacted audit gallery (hardened gains)
python scripts/hardened_supervision_showpiece.py
nex trace-gallery --redact --out /tmp/audit-gallery.md

# Drop-in for Cursor / Aider / your own tools (still gets policy + Grok + traces)
nex serve --model qwen3.5-9b --enable-mtp
```

The key unmet need this solves: You don't have to choose between "use the powerful agent I already know" and "have real safety + Grok intelligence + auditability." You get both.

See the live demo script and video outline below for the exact "agent tries something dangerous → policy blocks or Grok reviews → safe path taken → full replay" flow.

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
- **New hardened reproducible showpiece** (the one to run on a fresh clone): `scripts/hardened_supervision_showpiece.py`
- **Ready-to-record video script** (90-120s, designed to make Elon/xAI sit up): `docs/grok_in_loop_demo_video_script.md`

The video script and landing page are built around the *unique* "needs first" story above. Run the hardened showpiece script after `git clone + uv install` to see the gains proven on a clean copy.

---

## Make Elon Proud — Why This Matters (Needs That Actually Move the Mission)

xAI's mission is to understand the universe. That requires builders who can use powerful agents at scale without creating new centralization, cost, privacy, or safety problems.

This stack directly serves that by solving needs that are currently unmet at the intersection of local hardware, frontier models, and real agentic workflows:

- **Efficiency that scales**: The only practical way to get near-frontier agent performance while keeping most tokens on-device (OptiQ + MTP) and only escalating to Grok when it adds real value. This is the tokens-per-watt / energy reality that will determine whether agentic systems can be ubiquitous (cars, robots, personal devices) rather than just another cloud service.
- **Auditable autonomy at scale**: Agents that can act in the world (or on your codebase) but with deterministic policy, declared effects (MCP-Cortex), continuous enforcement, rollback, and traces that distinguish "what the local model decided" vs "what Grok decided." This is the safety/oversight layer that will be required for anything like Optimus-scale deployment or high-stakes software work.
- **Grok as the actual intelligence layer, not just another model**: Built with Grok. Uses Grok for the hard parts. Designed so that local efficient agents become a multiplier for Grok rather than a competitor or a diluted version.
- **Truth-seeking by default**: Policy before LLM judgment. Structured contracts and traces. Replayable evidence. Maximum truth about what actually happened, not "the model said it was fine."
- **Anti-bloat engineering culture**: uv-first, real code, no mocks, small focused modules, honest boundaries. The velocity and rigor that xAI itself embodies.

This is not another local LLM tool. It is infrastructure for the agentic era that aligns with how xAI thinks about capability, efficiency, truth, and building the future.

---

## The "Extra Big Wow" (What Changes the Game)

The killer unmet need: People already have powerful daily drivers (Claude Code, Cursor/Codex, Aider, etc.). They don't want to switch to a new "local-only" agent.

**Only this stack lets you keep using the agents you already love — while giving them Grok-level judgment on hard calls, Sentinel-grade policy safety, MCP-structured tool effects, and full local-vs-Grok traces.**

```bash
# Today
claude .                    # powerful, but risky + expensive + no real audit

# With this
grok-claude .               # same interface, now under full policy + Grok escalation + traces
# or
nex supervise claude .      # same thing, unified command
```

This is the feature no one else can credibly offer yet, because no one else has the full fusion (local OptiQ speed + real Grok + policy/enforcer/rollback + MCP contracts + PTY-level control of external agents + unified traces).

---

## Current High-Leverage Features (All Implemented, All Needs-Based)

(From the original plan + Grok-in-the-Loop fusion session)

- Multi-model OptiQ registry with MTP speculative decoding → addresses efficiency/privacy/cost needs on Apple Silicon hardware.
- Autonomous agent with safe sandbox tools + MCP-Cortex contracts → addresses safe tool use + declared effects needs.
- Production Textual TUI (real multi-turn, live model/MTP switching, tool pane, Grok escalation visibility) + richer approval queue concepts → addresses human-in-the-loop + visibility needs.
- Full OpenAI-compatible server (with tool_calls passthrough) → addresses "use with the tools I already have" need.
- First-class supervision of external agents (`nex supervise claude .`, `grok-claude`, `grok-codex`, etc.) borrowing PTY runner, trust prompt injection, interaction harnesses, and approval queue from gemOptq → directly solves "use the agents I already love, but make them safe and smarter."
- GrokEscalator + GrokAugmentedAuditor (local OptiQ fast path + real xAI Grok for review cases) → addresses the hybrid intelligence need.
- SentinelPolicy + **real ContinuousEnforcer + FileEffectObserver** (ported/adapted, now with live fs diffs) with rollback → addresses the deterministic safety + recovery need.
- Unified trace viewer (`nex trace replay`) + **`nex trace-gallery`** (redacted, shareable MD/HTML artifacts) that shows local vs Grok decisions → addresses the auditability + learning + team-proof need.
- **One-command permanent wrapper** (`nex supervise --install`) + live TUI approvals queue (PendingApproval + a/b/o keys) + end-of-run Oversight & Efficiency Reports → directly solves "use the agents I already love, but make them safe, visible, and auditable forever with zero workflow change".
- `nex models download | recommend | set-override`, `nex self update | status | doctor` (uv-aware), plugin system, history RAG — all supporting the core needs.

See `ARCHITECTURE_MERGE.md` for exactly how the two repos combine to deliver capabilities no single project has.

---

## Quick Start (Tested on Fresh Clone From GitHub)

```bash
# Fresh clone + modern uv path (recommended)
git clone https://github.com/deesatzed/OptiqMTPMLX.git
cd OptiqMTPMLX
uv venv .venv
uv pip install -e '.[server,tui,rag]'

# The hybrid "Grok in the Loop" experience (addresses hybrid intelligence + safety needs)
GROK_IN_LOOP=true nex agent "Your real goal here"

# The Extra Big Wow — supervise the agents you already use
nex supervise claude .                    # or grok-claude .
grok-codex .                              # Cursor-style under the same layer

# Beautiful TUI with live supervision
./run.sh tui

# OpenAI server (point Cursor/Aider/your tools at it — still gets policy + Grok + traces)
nex serve --model qwen3.5-9b --enable-mtp
```

Requires Apple Silicon Mac with Metal. XAI_API_KEY optional (full escalation when present; graceful fallback otherwise).

---

## Showpiece & Demo Assets (Needs-First, Attention-Grabbing)

- **Polished landing page**: `docs/index.html` (open directly or `cd docs && python -m http.server 8080`). Leads with real user pains, "only this stack" unique value, and the external supervision story.
- **Detailed showpiece brief**: `docs/showpiece/optiq-mtp-mlx.md` — the "why this exists" document written around unmet needs.
- **Ready-to-record video script**: `docs/grok_in_loop_demo_video_script.md` (optimized for X + YouTube, with scenes that start from pain and end on the meta "built with Grok for the xAI era" + efficiency + auditable autonomy angles).

---

## Make Elon / xAI Proud — Direct Alignment

This directly serves the mission by giving builders a tool that is:
- **Efficient** at the hardware level (the only way agentic systems become ubiquitous instead of another cloud cost center).
- **Auditable and safe by design** (the layer that will be required for anything like Optimus-scale or high-volume software autonomy).
- **Grok-native** (uses real Grok for the parts where it is uniquely valuable; the whole project was built with Grok).
- **Truth-seeking** (policy before judgment, structured contracts, replayable evidence, honest boundaries).
- **Anti-bloat, maximum velocity** (uv-first, real code, no mocks, small focused modules).

This is infrastructure for the agentic era that aligns with how xAI thinks.

---

## Next (Keep Pushing)

The fusion is the moat. The "Extra Big Wow" is the ability to safely supervise the agents people *already* use, with Grok as the intelligent layer.

If you want to keep going on any of the remaining items (deeper live TUI supervision dashboard with side-by-side Grok panel + approval queue, public redacted trace gallery, one-command "turn my existing Cursor into a Grok-in-the-Loop version", live efficiency widget, actual end-to-end recording of a real Claude Code session under the new grok-claude wrapper, etc.), just say the word.

We're building the thing that should exist. Needs first. Only-we-can capabilities. Maximum truth.

Clone it. Run it under Grok in the Loop. Look at the trace. Build the future safely and efficiently.

Built with Grok. For the xAI era.

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
