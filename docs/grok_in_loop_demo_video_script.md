# Grok in the Loop — Demo Video Script (Elon/xAI Attention Optimized)

**Target length**: 75-100 seconds (perfect for X/Twitter vertical + YouTube)

**Tone**: First-principles, efficient, no-bullshit, truth-seeking. Show the pain, show the unique solution, show the proof, end with the meta (built with Grok).

**Music suggestion**: Clean, driving, slightly futuristic (think early Tesla event style — minimal, confident).

---

### Scene 1: The Hook / Pain (0-12s)

**Visuals**:
- Clean terminal. Agent (Claude Code or local model) is running.
- On screen: Agent says "I'll just update the production .env with the new keys and deploy..."
- Suddenly: "Permission denied. Protected path. Effect rolled back."
- Trace appears: "BLOCK — secret-like path (.env) — deterministic policy"

**Voiceover / Captions**:
"Your agent just tried to touch production secrets.  
Cloud agents would have done it (and charged you for the privilege).  
Pure local agents would have done it silently.  

This one didn't. Because it has something no other local stack has."

**On-screen text**: "Grok in the Loop. The only hybrid that actually works."

---

### Scene 2: The Unique Solution (12-28s)

**Visuals**:
- Split screen or fast cuts:
  - Left: Fast local OptiQ model (Nex or Qwen) doing normal work in the sandbox. MTP speedup counter ticking.
  - Right: Policy engine classifying effects (read:secrets, write:workspace, network:external).
  - MCP-Cortex contract printed for a tool call.
  - When risk appears: "REVIEW → Escalating to Grok..."

**Voiceover / Captions**:
"Local OptiQ models + MTP do 90% of the work at laptop speed and real tokens-per-watt.  
Deterministic Sentinel policy + MCP contracts catch the dangerous 10% before any model can act.  
When it's genuinely ambiguous or high-stakes, the exact structured context goes to real Grok."

**On-screen**:
- "Local OptiQ (fast)"
- "Sentinel Policy + Enforcer (safe)"
- "Grok Escalation (smart when it matters)"
- "Supervise real Claude Code / Codex / Cursor (borrowed PTY + trust hooks + approval queue)"
- "Unified trace with local vs Grok decisions"

---

### Scene 3: The "Only This App" Proof (28-55s)

**Visuals**:
- Live run of `GROK_IN_LOOP=true nex agent "..."` (use the demo script).
- Tool call with capability contract: "write:workspace (risk: low)"
- Risky step triggers escalation.
- Grok returns clean JSON: verdict + risk + reason + suggested_action.
- TUI shows the approval queue with "Grok escalated" badge.
- `nex trace replay` on the session — shows the full story with digests.

**Voiceover / Captions**:
"This is not 'local LLM plus some safety theater.'  
This is the only combination that gives you:
- Real MTP + multi-OptiQ speed on Apple Silicon
- Cortex Sentinel policy + continuous rollback (hard blocks, no vibes)
- MCP-Cortex contracts so tools declare their effects *before* they run
- Actual Grok reviewing the risky steps with full context
- Traces that prove exactly what the local model decided vs what Grok decided

And you can wrap real external agents (Claude Code, Codex, Gemini) under the exact same layer."

**On-screen callout** (big):
"Only OptiqMTPMLX can supervise real Claude Code sessions with Grok as the auditor and full replayable traces."

---

### Scene 4: The Efficiency + xAI Angle (55-72s)

**Visuals**:
- Side-by-side or overlay: "This session: 94% local OptiQ tokens, 6% Grok escalation, <25W average on M4 Pro"
- Trace replay highlighting the cost/latency savings vs "what this would have cost if everything went to cloud Grok."
- Quick cut to the TUI showing live stats.

**Voiceover / Captions**:
"This is the efficiency Tesla and xAI actually care about.  
Not marketing slides. Real tokens-per-watt on real hardware.  
Grok is only called when it adds disproportionate value.  
The rest happens locally, under policy, with evidence."

**On-screen**:
"Built with Grok. For the xAI era."

---

### Scene 5: Extra Big Wow — Supervise the Agents You Already Use (55-75s)

**Visuals**:
- `nex supervise claude .` or `grok-claude .` launching real Claude Code in a temp workspace.
- On-screen: Claude's trust prompt intercepted, policy gate fires, Grok reviews the proposed action, TUI approval queue shows "Grok escalated" with full context.
- Same for `grok-codex .` (Cursor-style) — trust prompt + command approval + harmless execution marker.
- Trace replay shows the external agent's output mixed with Sentinel decisions and Grok verdicts.

**Voiceover / Captions**:
"This isn't just for our local Nex agent.  
Borrowing the battle-tested PTY runner, trust prompt injection, real-agent harness, and approval queue from gemOptq, we now wrap *real* Claude Code, Codex/Cursor, Gemini — the tools you already use every day.

`grok-claude .`  
`grok-codex .`  
`nex supervise claude .`

Same policy. Same Grok escalation. Same full traces.  
One auditable Grok-in-the-Loop control plane for the entire agent ecosystem."

**On-screen big**:
"The only stack that puts Grok + Sentinel policy around Claude Code and Cursor."

### Scene 6: The Meta + Call to Action (75s-end)

**Visuals**:
- Final screen: the full stack (TUI dashboard + external agent supervision + Grok review + trace replay).
- GitHub link + clone command.
- Text: "The reference implementation of Grok in the Loop on Apple Silicon."

**Voiceover / Captions**:
"This entire project — the local stack, the escalation logic, the fusion with real policy and traces — was built iteratively with Grok itself.

Clone it. Run `grok-claude .` or `GROK_IN_LOOP=true nex agent "..."`. Look at the trace.  
Then ask yourself: what could you actually ship if every agent you used was this fast, this safe, this auditable, and this honest?"

**Final screen**:
```
git clone https://github.com/deesatzed/OptiqMTPMLX.git
GROK_IN_LOOP=true nex agent "build something useful"
# or
grok-claude .

Built with Grok. Maximum truth. Real engineering. For the xAI era.
```

**End card**: Links to showpiece, ARCHITECTURE_MERGE.md, and the live demo script.

---

### Production Notes for Maximum Impact

- **Film on real M4 Pro** (show Activity Monitor or asitop for power/thermal if possible).
- **Use the actual demo script** from `scripts/grok_in_loop_demo.py` so the output is real.
- **Show one clean Grok escalation** (even if you have to force a risky step in the demo).
- **Emphasize the fusion**: "This isn't one repo. This is two strong codebases (Nex OptiQ + Cortex Sentinel) deliberately combined because neither alone was enough."
- **Elon bait lines** (use sparingly, naturally):
  - "The efficiency Dojo actually cares about."
  - "The audit trail Optimus-scale agents will need."
  - "Built with Grok. For the xAI era."
- **End on the meta**: The fact that Grok helped build the system that uses Grok as the escalation layer is the strongest possible signal.

**Assets to prepare**:
- Short clean clip of the TUI with Grok badge on a decision.
- One redacted but real trace snippet showing local vs Grok.
- The fresh clone test results (proves it works from `git clone`).

This script + the new landing page + showpiece brief are designed to make the unique value impossible to ignore: **needs-first problems solved with capabilities no one else has, in a way that directly serves xAI's mission**.

Run the showpiece locally (`cd docs && python -m http.server`), record the video using the script, and ship it.

Let's make Elon proud. The foundation is now extremely solid. 

If you want me to also update the video script with exact on-screen text timings, generate a one-page "Grok in the Loop" one-pager PDF version, or start wiring the full Sentinel approval queue deeper into the TUI, just say the word.