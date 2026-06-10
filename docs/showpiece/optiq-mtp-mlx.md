# OptiqMTPMLX Showpiece — Grok in the Loop

**The reference implementation of what agentic AI should actually feel like in 2026.**

## The Core Need

Developers want to use powerful autonomous agents (Claude Code, Cursor, Aider, custom MCP agents, or their own local models) to ship faster.

What they actually get today is a terrible set of compromises:

- Cloud agents: every action leaks context, costs money, has latency, and you have zero control when the model decides to do something stupid.
- Pure local agents: fast and private until they touch a secret, propose a bad deploy, or slowly drift from the actual goal — with no audit trail and no way to get frontier-quality judgment on the hard parts.
- No real middle path that combines local efficiency, frontier reasoning only where it matters, deterministic safety rails, and provable auditability.

**xAI's mission is to understand the universe.** Tools that multiply human (and AI) capability should not create new risks or multiply cost. They should be efficient, auditable, and honest about their boundaries.

OptiqMTPMLX (Nex) is the first stack that actually solves this in a production-feeling way.

## The Unique "Only This App" Combination

No other project combines these capabilities:

1. **Native high-quality local inference on Apple Silicon** — Multi-model OptiQ-4bit registry (Nex-N2-Mini, Qwen3.5/3.6 series, Gemma-4, Nemotron, etc.) + MTP speculative decoding for real 1.3-1.5× decode speedup. Most work happens locally at laptop speed and low power.

2. **Grok as the smart escalation layer** — Local OptiQ models handle the routine 80-95%. When the deterministic policy or local auditor flags something as REVIEW (risky, ambiguous, high-stakes), the *exact* structured context is sent to real Grok (xAI API). You get frontier reasoning + a safer alternative, recorded in the trace with latency and reasoning.

3. **Cortex Sentinel-grade safety (ported concepts)** — Deterministic policy engine with hard blocks on protected paths, secrets, external network, and production deploys. Continuous enforcement + rollback. Structured `CapabilityContract`s via the MCP-Cortex adapter so tools declare their effects *before* they run.

4. **Unified, replayable, auditable traces** — Every decision (local policy, local auditor, Grok escalation, human action) is in one digest-verified log. The trace explicitly shows "local OptiQ decision" vs "Grok escalated" with full context. This is the kind of provenance real engineering teams and future large-scale autonomy will need.

5. **Production interfaces + Real External Agent Supervision** — Beautiful Textual TUI, full OpenAI-compatible server (drop-in for Cursor/Continue/Aider), MCP server. Plus first-class wrappers (`nex supervise claude .`, `grok-claude .`, `grok-codex .`) that borrow PTY runner, trust prompt injection, interaction harnesses, and approval queue patterns directly from gemOptq's proven real_agent_smoke, PtyAgentRunner, and SentinelTUI. Turn every agent you already love into a fully policy-gated, Grok-escalated, fully traced session under one auditable control plane. This is the "Extra Big Wow" feature: the universal safe supervisor for the entire AI coding agent ecosystem.

This is not "local LLM + some safety." This is the deliberate fusion of the best local efficiency stack with the best local supervision stack, with real Grok as the high-quality backstop.

## What It Actually Demonstrates Today

- `GROK_IN_LOOP=true nex agent "..."` — Real hybrid execution. Tool calls emit MCP-Cortex-style contracts. Risky steps escalate to Grok. Full trace is produced.
- Real external agent supervision (via the fused Sentinel PTY + policy layer from gemOptq).
- Live model switching, MTP toggle, and Grok escalation visibility in the TUI.
- `nex serve` as a local backend that any agent tool can point at while still getting policy + Grok oversight.
- `nex trace replay` that makes the entire local-vs-Grok decision tree inspectable.

## The "Wow" That Grabs Attention

- **Efficiency theater that actually matters**: Local OptiQ + MTP does the boring work at 10-50× better tokens-per-watt than always hitting Grok. Grok is only invoked when it adds disproportionate value. This is Tesla/Dojo language.
- **Grok reviewing its own local work**: The meta property. Local models do the heavy lifting. Grok (the model that helped build this) reviews the risky steps with full context. Very few systems can credibly claim this.
- **Real external agents under GrokSentinel**: You can take an actual Claude Code or Codex session and put it under the same policy + Grok escalation + trace layer. This feels production-grade, not toy.
- **Auditability that survives scrutiny**: Structured contracts, deterministic policy before any LLM judgment, rollback events, and traces that separate local vs Grok decisions with digests. This is the kind of infrastructure that makes large-scale agentic systems defensible.
- **xAI-native by construction**: Built with Grok. Uses Grok for the parts where Grok is uniquely good. Designed to multiply xAI's mission without creating new centralization or risk.

## Positioning for Maximum Attention (Elon/xAI)

- **For xAI**: The reference local runtime that lets builders get Grok-quality results without sending everything to the cloud, while adding the safety and audit layers that real deployment will require.
- **For Tesla/Optimus**: A concrete example of efficient on-device intelligence + policy guardrails + auditable escalation to a stronger model. The same pattern that will matter at fleet scale.
- **For developers**: Finally, an agent supervisor that is fast *and* trustworthy *and* gets smarter when it needs to — without the usual compromises.
- **Meta**: This entire project (including the Grok escalation logic and the fusion plan) was built iteratively with Grok itself. That is the product.

## Current Assets (Ready to Use)

- Modern single-file landing page: `docs/index.html`
- Detailed showpiece brief: `docs/showpiece/optiq-mtp-mlx.md`
- 90-120s demo video script optimized for attention: `docs/grok_in_loop_demo_video_script.md`
- Full architecture fusion document: `ARCHITECTURE_MERGE.md`
- Working code with the hybrid loop, policy, contracts, traces, TUI, and servers (tested on fresh clone from GitHub).

## How to Experience It

```bash
git clone https://github.com/deesatzed/OptiqMTPMLX.git
cd OptiqMTPMLX
uv venv .venv
uv pip install -e '.[server,tui,rag]'

GROK_IN_LOOP=true nex agent "Create hello.txt in the sandbox and verify the content"
```

Open `docs/index.html` or serve the docs folder for the polished landing experience.

---

This is the kind of thing that makes the future arrive faster, more efficiently, and with eyes wide open.

Built with Grok. For the xAI era. Maximum truth. Real engineering. No bloat. 

Let's keep going.