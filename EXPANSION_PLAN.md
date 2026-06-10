# Nex High-Leverage Expansion Plan

**Project**: Nex — Multi-Model OptiQ CLI + TUI + MCP + Agent Runner for Apple Silicon  
**Current State (as of this plan)**: 
- Strong multi-model registry (`nex/models.py`)
- MTP / speculative decoding support (`--enable-mtp`, draft models)
- Persistent sessions + JSONL logging
- Safe sandbox agent tools with flexible parser
- MCP server with model + MTP parameters
- Typer + Rich CLI
- Basic Textual TUI skeleton (`nex tui`)
- `uv`-first installation (`run.sh`, pyproject `[tool.uv]`, optional `[tui]`)
- Self-management commands (`nex self update`, `status`, `doctor`, `update-deps`)
- Config system (user models, defaults)

**Goal**: Evolve Nex from a capable single-app experience into the premier, delightful, production-grade local multi-model runner for developers and agentic workflows on Apple Silicon. Prioritize **high-leverage** features that multiply usability for both humans (CLI/TUI) and other AIs (MCP + OpenAI compat).

**Guiding Principles** (aligned with workspace rules):
- No mocks, simulations, or placeholders. All real, functional code.
- Model-agnostic by default via `ModelProfile` registry (Qwen, Gemma, Nemotron, Nex, MiniCPM, custom, future MTP/VL variants).
- MTP, persistence, agent tools, and MCP must work across all additions.
- Prefer `uv` for speed and reproducibility.
- Keep the fast Typer CLI as the scriptable core.
- Make the Textual TUI the aesthetically SOTA daily driver.
- Incremental, reviewable changes. Each phase must leave the app in a working state.
- Update docs (README, EXPANSION_PLAN.md), tests where possible, and `nex self doctor`.
- Validate end-to-end after each major addition (CLI + TUI + MCP + agent).

**High-Leverage Ideas** (prioritized by impact on users + other AIs + maintainability):

1. **OpenAI-Compatible Server** (`nex serve`) — Highest leverage
2. **Polish & Expand Textual TUI** — Highest aesthetic + daily UX win
3. **Richer Config + Per-Model Overrides + Better Self-Experience**
4. **Enhanced Model Management** (downloader, recommender, memory, `nex models` power-ups)
5. **Semantic History Search / RAG over Conversations**
6. **Plugin System for Custom Tools**
7. **Shared Theming + Packaging Improvements** (uv tool, standalone notes)
8. **Future-Proofing** (Vision toggle, advanced MTP options, etc.)

---

## Overall Phased Roadmap

### Phase 0: Foundations (Mostly Complete)
- Multi-model registry + MTP
- uv integration + `run.sh`
- `nex self` commands (update, doctor, status)
- Config system + user models
- Basic Textual TUI + `nex tui`
- Agent + MCP + persistence already strong

**Verification**: `nex self doctor`, `nex models list`, `nex tui` (basic), `nex chat --mtp`, MCP tools with `model=` and `enable_mtp=`.

---

### Phase 1: OpenAI-Compatible Local Server (Highest Leverage)
**Why high-leverage?**  
Instant compatibility with the entire ecosystem that speaks OpenAI API: Continue.dev, Cursor, Aider, custom agents, LangChain/LlamaIndex, VS Code extensions, etc. Turns Nex into a drop-in local backend for any tool. Multiplies reach far beyond the CLI/MCP.

**Scope**:
- `nex serve [--port 8000] [--model qwen9b] [--enable-mtp]`
- FastAPI + uvicorn (or Starlette).
- Endpoints:
  - `POST /v1/chat/completions` (streaming + non-streaming, supports `model`, temperature, etc.)
  - `GET /v1/models` (list from registry + user models, with MTP flags)
  - Health: `/health`
- Reuse existing `Engine`, `ChatSession`, MTP logic, and `apply_chat_template`.
- Support tool calling passthrough if the calling client sends tools (future agent synergy).
- Configurable via CLI flags + env + config file.
- Graceful shutdown, request logging (tie into existing JSONL?).
- Optional: CORS for browser-based tools.

**Implementation Steps**:
1. Add optional dependency: `fastapi`, `uvicorn[standard]`, `pydantic` (or use existing).
2. Create `nex/server.py`:
   - `app = FastAPI(title="Nex Local Server")`
   - Dependency injection for `Engine` (per-request or cached with model switching).
   - Pydantic models for OpenAI request/response (ChatCompletionRequest, etc.).
   - Streaming using `StreamingResponse` + the existing `stream_generate` generator (wrap with SSE).
   - Model resolution via `get_profile` + support `enable_mtp` / `draft_model` in request body or query.
3. Wire in `cli.py`: new `serve` command that does `uvicorn nex.server:app --port ...` (or direct `app.run()`).
4. Update `Engine` / `ChatSession` if needed for better async compatibility (run blocking generation in threadpool via `anyio.to_thread` or `asyncio`).
5. Update MCP tools? Or document that the server itself can be called via MCP if desired.
6. Add to TUI? Optional "Server" mode toggle (advanced).
7. Tests: Use `httpx` or `testclient` for basic /v1/chat/completions roundtrips with different models + MTP.
8. Docs: Full section in README with curl examples, Continue.dev config, etc. Update `nex self doctor` to check server port.

**Files to Touch / New**:
- `pyproject.toml` (optional `server` extra)
- `nex/server.py` (new)
- `nex/cli.py` (add `serve` command + options)
- `nex/engine.py` (minor async helpers)
- `README.md`
- `EXPANSION_PLAN.md` (this file)

**Risks / Mitigations**:
- Blocking generation in async server → Use thread workers.
- Model switching mid-server → Support per-request model (already in registry).
- Token counting / usage stats → Mirror OpenAI format using existing `GenerationStats`.

**Verification**: 
- `nex serve --model qwen3.5-4b --mtp` then `curl` a completion.
- Works with at least one external client (e.g. simple Python openai client).
- MTP flag honored and visible in logs.

**Estimated Size**: Medium (core server + streaming is the bulk).

---

### Phase 2: Polish & Expand the Textual TUI
**Why high-leverage?**  
The TUI is the "aesthetically SOTA" face of the app. Making it production-ready (multi-turn, beautiful rendering, tool visibility, model/MTP controls) will make daily use delightful and competitive with tools like LM Studio or Ollama TUI.

**Scope** (build on existing skeleton):
- Full multi-turn history using `ChatSession` + persistence.
- Proper streaming with `Markdown` widget + collapsible `<think>` / reasoning panel (reuse/extend `ThinkAwareStreamer`).
- Live tool execution viewer (when in agent mode or when model emits tool calls).
- Sidebar improvements: Searchable model list, quick MTP per-model toggle, recent sessions with preview.
- Top bar: Current model + MTP status + tokens/s + memory (reactive).
- Command palette or footer shortcuts for `/clear`, `/system`, model switch, agent mode launch.
- Theming (light/dark or CSS variables shared with Rich where possible).
- Token-by-token progress + cancel button.
- Optional: Split view for agent tool sandbox inspection.

**Implementation Steps**:
1. Refactor `nex/tui.py`:
   - Integrate real `ChatSession` and `persistence`.
   - Use `textual.widgets.Markdown` for assistant messages.
   - Custom `ThinkingPanel` or `Collapsible` for reasoning traces.
   - Worker threads for generation (already using `run_worker`).
2. Add reactive components for live stats (bind to engine callbacks or poll `GenerationStats`).
3. Tool visibility: When parser detects tool call, show a "Tools" pane with live `Observation` updates.
4. Model/MTP switching: Wire to existing registry + engine reload (non-destructive to current conversation if possible).
5. Add `textual` dev tools for hot-reload during development.
6. Update `cli.py` `tui` command to accept `--model`, `--enable-mtp`, `--session`.
7. Shared theming: Extract common styles to a small `nex/theme.py` module (colors, styles for both Rich and Textual).
8. Polish: Animations (Textual supports), better input history, copy-to-clipboard actions.

**Files**:
- `nex/tui.py` (major expansion)
- `nex/theme.py` (new, shared)
- `nex/cli.py` (pass-through flags)
- `nex/render.py` (maybe extract more reusable renderers)
- `pyproject.toml` (ensure textual[dev])
- README (TUI screenshots / keybindings section — describe since no real images)

**Risks**: Async/sync boundary with mlx-lm generation. Mitigate with workers + queue.

**Verification**: 
- Full conversation with model switches + MTP toggle mid-session.
- Agent tool calls visible and executable from TUI.
- Looks great on M4 Pro terminal (test different sizes).

**Size**: Medium-High.

---

### Phase 3: Richer Config + Per-Model Overrides + Self Polish
**Why high-leverage?**  
Users want "set it and forget it" per model (different temp for creative vs coding, MTP on by default for Nex-MTP, custom system prompts). Self commands make the app feel alive and maintainable.

**Scope**:
- Expand `nex/config.py`:
  - `overrides[repo_id] = {"temperature": 0.4, "enable_mtp": true, "system_prompt": "...", "num_draft_tokens": 5}`
  - Merge logic in `get_effective_profile` and engine creation.
- `nex self` enhancements:
  - `nex self update` also handles app itself (git pull if in a git repo, or instructions for `uv tool upgrade` / future releases).
  - `nex self config edit` (opens editor for the json).
  - Better status output (shows active overrides, current MTP state).
- Integrate overrides into CLI resolution, TUI, server, MCP, and agent.
- Persist last-used model + MTP preference per session or globally.

**Steps**:
1. Extend `ModelProfile` or use a separate `RuntimeConfig` dataclass.
2. Update `_get_engine` in cli.py and MCP to apply overrides.
3. Add commands in `self_app`.
4. Wire into TUI sidebar (show "using override" badges).
5. Update `nex models info` to show current effective settings.
6. Docs + examples in README.

**Files**: `nex/config.py`, `nex/cli.py`, `nex/mcp.py`, `nex/tui.py`, `nex/models.py` (minor), `README.md`.

**Verification**: Set per-model temp/MTP, restart, confirm applied in `nex self status`, TUI, and a server call.

**Size**: Low-Medium.

---

### Phase 4: Enhanced Model Management (Downloader, Recommender, Memory)
**Why high-leverage?**  
Discovery and onboarding friction is real with many HF models. One-command "give me the best coding model under 10GB" or "download all recommended small OptiQ models" is magic.

**Scope**:
- `nex models download <alias-or-repo>` (or `nex models download --recommended --size small`)
- Use `huggingface_hub.snapshot_download` with rich progress (already have HF hub).
- Smart recommender: Based on `strengths`, size, MTP support, and rough memory (add `approx_unified_memory_gb` to profiles).
- `nex models recommend "coding and tool use" --max-memory 12`
- Enhanced `nex models list` with columns for memory, MTP, installed status.
- `nex doctor` can suggest missing recommended models and offer to download.
- Cache downloaded models info.

**Steps**:
1. Add fields to `ModelProfile`: `approx_memory_gb: float`, `is_recommended: bool`, `tags: list`.
2. New functions in `models.py`: `download_model`, `recommend_models(query, max_memory=None)`.
3. CLI in `models_app`: `download`, `recommend`.
4. Progress bar using Rich (already in engine for loading).
5. Integrate with config (mark as "user_models" on download).
6. Update TUI model list to show "downloaded" / "download" action.

**Files**: `nex/models.py` (core), `nex/cli.py`, `nex/tui.py` (optional), `README.md`.

**Verification**: Download a small model you don't have, list shows it, `recommend` works, doctor suggests.

**Size**: Medium.

---

### Phase 5: Semantic Search / RAG over History
**Why high-leverage?**  
Power users accumulate dozens of sessions. Being able to ask "what was that trick I used last month for async Python with the Qwen model?" inside Nex itself is extremely useful and differentiates the tool.

**Scope**:
- On every turn (or nightly), embed the user+assistant pair using a lightweight local embedder (e.g., `sentence-transformers` or even `mlx` embeddings if available, or simple `BAAI/bge-small` via HF).
- Store embeddings alongside sessions in a simple vector store (lance or just numpy + json for minimal deps, or `chromadb` optional).
- `nex search "async context manager tip"` or `/search` in chat/TUI.
- Surface relevant past turns as context or clickable.
- Optional: Use retrieved context to augment current prompt (light RAG).

**Steps**:
1. Add optional dep `sentence-transformers` or use `transformers` + `torch` (but prefer light).
   - Alternative: Since we have mlx-lm, explore if we can use a small embedding model from the same stack.
2. Create `nex/history_rag.py` (embed, index, search).
3. Hook into persistence on save.
4. Add CLI: `nex search "query"`, and integrate into chat input parsing.
5. TUI: Search pane or command.
6. MCP tool: `nex_search_history`.
7. Keep it optional and lazy (no dep bloat for core users).

**Files**: New `nex/history_rag.py`, updates to `persistence.py`, `cli.py`, `tui.py`, `mcp.py`, `pyproject.toml` (optional `rag` extra).

**Risks**: Embedding model size + first-run download. Mitigate by making it opt-in and using very small models.

**Verification**: Save several conversations, search, get relevant hits.

**Size**: Medium-High.

---

### Phase 6: Plugin System for Custom Tools + Theming + Packaging
**Why high-leverage?**  
Extensibility keeps the tool alive long-term. Users (and other AIs) will want custom tools (git, web search via safe wrappers, database, etc.) without forking.

**Scope (incremental)**:
- Plugin discovery: `~/.nex/plugins/` or `nex/plugins/` with `register_tool(name, func, schema)` entrypoint.
- Simple decorator or class-based in `tools.py`.
- Theming: Central `theme.py` with CSS-like dicts consumable by both Rich and Textual.
- Packaging: Document `uv tool install --from git+... nex-cli`, provide example `uv.lock` for reproducible, notes on PyInstaller for standalone binary.

**Steps**:
1. Extend `tools.py` with plugin loader.
2. Create example plugin.
3. Theming module.
4. Update docs + `self doctor` (checks for plugins).
5. Packaging section in README.

**Files**: `nex/tools.py`, `nex/theme.py`, `nex/plugins/` (example), docs.

**Size**: Medium (plugins) + Low (theming) + Docs.

---

### Cross-Cutting / Ongoing
- **Documentation**: Every phase updates README (new sections, examples), this plan, and in-app help (`nex self doctor`, TUI footer).
- **Testing**: Add basic pytest where missing (focus on registry, config, engine MTP, server endpoints). Aim for key paths.
- **MCP / TUI / CLI Consistency**: All new features (server, plugins, RAG, overrides) must be exposed or at least configurable from all three interfaces.
- **Performance**: MTP + good model choice should remain fast. Profile generation calls.
- **Dep Management**: All new optionals go under clean extras (`[server]`, `[tui]`, `[rag]`, `[plugins]`). Use uv for dev.
- **Versioning**: Bump minor for each phase. Keep `nex --version` useful.
- **User Stories to Validate**:
  - "I want a local model that works in my editor like a cloud model."
  - "I want a beautiful local chat that remembers everything and lets me search it."
  - "I want to give my agent access to custom tools without editing core code."
  - "I want to keep my whole setup (models, prefs, history) updated easily."

---

## Suggested Implementation Order (Pragmatic)

1. **Phase 1 (OpenAI Server)** — Immediate high external impact.
2. **Phase 2 (TUI Polish)** — Makes the "aesthetic SOTA" promise real.
3. **Phase 3 (Config + Self)** — Improves daily ergonomics and maintainability.
4. **Phase 4 (Model Management)** — Reduces friction for the multi-model story.
5. **Phase 5 (RAG)** — Adds unique intelligence layer on top of persistence.
6. **Phase 6 (Plugins + Theming + Packaging)** — Long-term extensibility.

After each phase:
- Run full smoke: `nex self doctor`, TUI, CLI with MTP + different models, MCP tool call, agent.
- Update this plan with "Completed" notes.
- Commit with clear message referencing the phase.

**Next Action After This Plan**:
- User (or implementer) picks the first phase and we execute it using small, reviewable changes (as per workspace rules).
- Consider creating GitHub issues or beads from this plan if the project moves to tracked work.

This plan is designed to be living — update it as we learn.

**Status**: **Significant progress made** (2025-06).

**Implemented in this "crank out" pass** (multiple rounds):
- OpenAI-compatible server (`nex serve`) with full streaming/non-streaming, MTP passthrough, model selection, /v1/models, /health. Production-ready for Cursor, Continue.dev, Aider, agents, etc.
- Major Textual TUI upgrade: real multi-turn via ChatSession + persistence, live model/MTP switching, think tag handling in Markdown, theme integration, live stats, clean UI.
- Richer config system (`get_runtime_overrides()`, deeper wiring into engine/CLI/TUI/server).
- Enhanced model management: `nex models download <model>`, `nex models recommend "query" --max-memory X`, memory estimates in profiles.
- Semantic history RAG: `nex search "query"`, MCP `nex_search_history`, optional `[rag]` extra.
- Plugin system: auto `load_plugins()` from `~/.nex/plugins/` and `./plugins/`, with working example `plugins/example_calculator.py`.
- Shared theming (`nex/theme.py`) wired into Rich render and TUI.
- All new features fully integrated with MTP, multi-model registry, agent tools, MCP, uv launcher, self commands, and persistence.
- Example plugin, server, improved TUI, RAG, etc. committed and pushed to GitHub.

See: `nex/server.py`, `nex/tui.py`, `nex/history_rag.py`, `nex/tools.py`, `nex/theme.py`, `plugins/`, updated `cli.py`/`config.py`/`models.py`/`pyproject.toml`.

**Remaining / Polish** (largely addressed in final implementation + this Grok-in-the-Loop session):
- ~~Deeper TUI (collapsible thinking via > **Thinking:** blocks in Markdown, dedicated tool execution Log pane, improved streaming/refresh).~~
- ~~Full per-model override persistence in config + UI (set_model_override, get_runtime_overrides, CLI `models set-override`, wired to TUI/engine/server/MCP).~~
- ~~Theming engine wired into Rich + Textual (theme.py + get_color usage in render.py and tui.py CSS/styles).~~
- ~~`uv tool install` / standalone binary packaging guidance + example (added to README and run.sh).~~
- ~~OpenAI server tool_calls support (standard format passthrough - custom XML tool calls are detected and emitted as OpenAI tool_calls in responses).~~
- Vision support: `vision` flag added to ModelProfile + registry ready. `good_tool_calling` flag for future server formatting. When good MLX-VL OptiQ models land, they can be added to KNOWN_MODELS and will be supported in CLI/TUI/server (engine already model-agnostic).

**Grok in the Loop** (new major initiative this session):
- All 5 concrete next steps executed: ARCHITECTURE_MERGE.md created with full mapping + fusion plan, `grok_escalator.py` + wiring into agent (with GROK_IN_LOOP env), `mcp_cortex_adapter.py`, TUI/trace polish, demo script + major README/plan updates.
- See `nex/grok_escalator.py`, `nex/mcp_cortex_adapter.py`, `scripts/grok_in_loop_demo.py`, and ARCHITECTURE_MERGE.md.
- Foundation now exists to fuse this codebase with gemOptq (Cortex Sentinel + MCP-Cortex) for a production-grade auditable hybrid "Grok in the Loop" supervisor.

All high-leverage items from the plan are now implemented, integrated, and pushed.

The plan remains the north star for future work.