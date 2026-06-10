# Grok in the Loop - Demo Video Script

**Title**: "Grok in the Loop: Local Speed + Frontier Judgment with Full Audit Trail"

**Length**: 90-120 seconds (vertical for X/Twitter + horizontal for YouTube)

**Style**: Clean screen recording + voiceover (or text captions). Show terminal + TUI. End with GitHub link.

## Scene 1: Hook (0-10s)
- Screen: Clean terminal.
- Command: `GROK_IN_LOOP=true nex agent "Create a small FastAPI hello world in the sandbox, add a test, and verify it works."`
- Voiceover: "What if your local AI coding agent could do 95% of the work at laptop speed... but call in the real Grok for the decisions that matter?"
- Show fast local output.

## Scene 2: Local Work (10-30s)
- TUI or terminal shows agent steps using local OptiQ model (Nex or Qwen).
- Tool calls with MCP-Cortex contracts printed.
- "Local decision: allow (green)"
- Voiceover: "Fast local models with MTP speculative decoding handle the routine work in the safe sandbox. Full trace of every step."

## Scene 3: Escalation Trigger (30-50s)
- Agent proposes something risky (e.g. writing to .env or production-like path, or ambiguous shell).
- Policy triggers REVIEW.
- "Escalating to Grok..."
- Voiceover: "When policy or the local auditor flags risk, the exact structured context — intent, effects, trace, capability contract — is sent to real Grok."

## Scene 4: Grok Response (50-70s)
- Grok returns structured JSON: verdict, risk, reason, suggested_action.
- Example: "block" or "review with safer alternative".
- Trace now shows "Grok escalated | latency: 420ms | verdict: review"
- Voiceover: "Grok gives a clear, auditable verdict with reasoning. The trace records local vs Grok decisions for full replay."

## Scene 5: Human + TUI (70-90s)
- Switch to rich TUI showing approval queue (inspired by Sentinel).
- User approves or overrides.
- Agent continues safely or is blocked with rollback.
- "Unified trace replay" command shows the full story, including Grok's input.
- Voiceover: "Human stays in the loop. Everything is traceable."

## Scene 6: Trace Replay & Wow (90-110s)
- `nex trace replay session-xxx.jsonl`
- Shows mixed local/Grok events.
- "This entire session is replayable with cryptographic digests. Local efficiency + Grok intelligence + provable safety."

## Scene 7: Call to Action (110s-end)
- "Built with Grok. Fusing OptiQ local inference with Cortex Sentinel safety."
- Screen: GitHub link, `pip install -e '.[server,tui,rag]'`, `GROK_IN_LOOP=true nex tui`
- "Run real agents under Grok supervision. Today."

**Production Notes**:
- Use the `scripts/grok_in_loop_demo.py` as base.
- Record on M4 Pro to show real Metal performance.
- Highlight MTP speedup numbers if visible.
- End screen with ARCHITECTURE_MERGE.md and EXPANSION_PLAN.md links.

**Assets to prepare**:
- Short clip of TUI with approval panel.
- Grok API response example (redact key).
- Trace JSONL snippet.

This demo positions the project as the practical realization of "Grok in the Loop" for developers who want power without losing control.