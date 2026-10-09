# Context & Architectural Guidelines for AI Coding Assistants (BuscaTuNido Monorepo)

This document establishes the multi-agent orchestration architecture, token-efficiency rules, and development guidelines for **BuscaTuNido**.

---

## 1. Monorepo Structure & Submodules

The project is structured as a top-level repository managing two Git submodules and an AI orchestration engine:

```
busca-tunido/
├── .gitmodules                           # Git submodule configuration
├── web/                                  # Next.js frontend (submodule)
├── api/                                  # NestJS backend (submodule)
├── orchestrator/                         # Canonical CrewAI multi-agent orchestrator (Python + uv)
│   ├── config/                           # Declarative CrewAI agents and tasks YAML
│   ├── skills/                           # Canonical filesystem-based Skill packages (SKILL.md)
│   └── src/orchestrator/
│       ├── llm/                          # Custom AgyLLM adapter (gemini-3.8-flash-high)
│       ├── flow.py                       # BuscaTunidoFlow (CrewAI Flow with @start and @listen)
│       ├── crew.py                       # BuscaTunidoCrew (@CrewBase, @agent, @task)
│       └── tools/                        # Worktree, agy, discovery, and verification tools
├── justfile                              # Root task runner (just)
├── README.md                             # Minimal project overview
└── AGENTS.md                             # Monorepo agent rules and guidelines
```

---

## 2. Canonical CrewAI Architecture with Skills, Flows & AgyLLM

The orchestration engine follows the official, modern **CrewAI (`v1.15.22`)** architectural pattern:

### Three-Tier Architectural Specification

| Tier | Component | Implementation Pattern | Responsibilities & Invariants |
| :--- | :--- | :--- | :--- |
| **Tier 1: Flow Orchestration** | `BuscaTunidoFlow` | `crewai.flow.flow.Flow` | - `@start discover_specs`: Dynamically scans pending task specs in `web/tasks` and `api/tasks`<br>- `@listen(discover_specs) run_crew_pipeline`: Dispatches `BuscaTunidoCrew` across disjoint DAG waves<br>- `@listen(run_crew_pipeline) verify_quality_gate`: Triggers centralized quality gate checks |
| **Tier 2: Declarative Multi-Agent Crew** | `BuscaTunidoCrew` | `@CrewBase` | - Agent Definitions: `config/agents.yaml`<br>- Task Specifications: `config/tasks.yaml`<br>- Specialized Skills: `skills/worktree-orchestration`, `skills/token-efficient-coding`, `skills/centralized-quality-gate` |
| **Tier 3: Execution Runtime & LLM Adapter** | `AgyLLM` | `crewai.BaseLLM` subclass | - Model: `gemini-3.8-flash-high`<br>- Runtime: Antigravity CLI (`agy`) subagent execution<br>- Dependencies: Zero third-party API keys required |

### CrewAI Skills in the Filesystem:

CrewAI agents are augmented with domain expertise via `SKILL.md` packages:

1. `skills/worktree-orchestration/SKILL.md`: Guides `lead_orchestrator` on DAG wave planning, file set disjointness ($Files(A) \cap Files(B) = \emptyset$), and worktree isolation with `wt`.
2. `skills/token-efficient-coding/SKILL.md`: Guides `code_worker` on token efficiency: strictly no heavy build/check tools, standard strict typing, no code comments, and targeted commits.
3. `skills/centralized-quality-gate/SKILL.md`: Guides `quality_integrator` on merging branches and running centralized quality verification in a single pass.

### Critical Worker Rules:

1. **No Slow Commands**: Workers MUST NOT execute `pnpm build`, `tsc`, `nest build`, `biome check`, or `git stash`. These commands pollute the context window with thousands of terminal tokens.
2. **Pure Implementation**: Workers focus exclusively on writing strictly-typed code for their designated files.
3. **Targeted Staging**: Workers only run `git add <file1> <file2>`, followed by a single-line conventional commit.

### Orchestrator / Integrator Quality Gate:

The Orchestrator runs all checks centrally on the merged integration branch in one pass:

1. `pnpm run check`: Global Biome formatting and auto-fixing in milliseconds.
2. Static type verification (Decoupled Incremental Typecheck):
   - `web`: `pnpm exec tsc --noEmit` (incremental with `.tsbuildinfo`).
   - `api`: `pnpm exec tsc --noEmit -p tsconfig.build.json` (incremental with `.tsbuildinfo`, skipping redundant `prisma generate` unless `schema.prisma` changed).
3. `pnpm run review`: Verification exit-code check.
4. `pnpm vitest run`: Unit tests.

### Worker Dispatch Specification (`agy` CLI):

The Orchestrator dispatches worker agents using the Antigravity CLI (`agy`) with strict invocation parameters:

1. **Workspace Root Anchoring**: Must pass `--add-dir <worktree_path>` so that file creation and edits target the isolated worktree directory instead of default global scratch paths.
2. **Reliable Model Selection**: Explicitly invoke `--model gemini-3.8-flash-high` for rapid response times and consistent availability.
3. **Execution Flags**: Use `-p <prompt> --mode accept-edits --dangerously-skip-permissions`.

### Orchestrator Pipeline Commands (`just`):

All orchestration routines are driven from the repository root via `just`:

- `just discover`: Dynamically discover pending task specifications and their active waves with DAG topological sorting.
- `just run-flow`: Execute the end-to-end canonical CrewAI Flow (`BuscaTunidoFlow`) with concurrent worktree dispatch, blast radius inspection, self-healing, and automatic archiving.
- `just heal [target]`: Run the centralized quality gate with automated self-healing repair loops.
- `just new-task [repo] [slug] [title]`: Scaffold a new valid markdown task specification adhering to domain standards.
- `just sync-submodules`: Synchronize and commit updated `web` and `api` submodule pointers in root monorepo.
- `just archive [repo] [task]`: Archive a completed task specification into `tasks/completed/` with sequential 3-digit indexing.
- `just plan [requirement]`: Run autonomous wave planning and worktree allocation via `BuscaTunidoCrew`.
- `just verify [target]`: Run the centralized quality gate (`web`, `api`, or `both`) on-demand.
- `just worktrees [repo]`: List active worktrees in `web` or `api`.

---

## 3. Worktree Management with Worktrunk (`wt`)

All parallel worktrees are strictly isolated within the git-ignored `trees/` directory (`trees/<repo>.<branch-name>`) to keep the monorepo root and submodule directories clean.

Worktree layout configuration is centrally declared in `orchestrator/config/wt.toml`:
```toml
worktree-path = "{{ repo_path }}/../trees/{{ repo }}.{{ branch | sanitize }}"
```
This configuration is automatically injected via `export WORKTRUNK_CONFIG_PATH` in `justfile` and passed in CrewAI tools:

- **Create**: `just wt-switch <web|api> <branch-name>` (or `wt -C <web|api> --config orchestrator/config/wt.toml switch --create <branch-name>`)
- **Inspect**: `just worktrees <web|api>` (or `wt -C <web|api> --config orchestrator/config/wt.toml list`)
- **Integrate / Merge**: `just wt-merge <web|api> <branch-name>` (or `wt -C <web|api> merge <branch-name>`)
- **Teardown**: `just wt-remove <web|api> <branch-name>` (or `wt -C <web|api> --config orchestrator/config/wt.toml remove --force <branch-name> -D`)

CrewAI tools in `orchestrator/src/orchestrator/tools/git_worktree_tools.py` wrap `wt` directly to guarantee deterministic worktree isolation inside `trees/` and clean lifecycle teardown.

---

## 4. General Development Constraints

1. **No Code Comments**: Do not write comments inside code unless explicitly requested by the user. Use descriptive naming and explicit types instead.
2. **No Direct Config Edits**: Never modify `package.json`, `pnpm-lock.yaml`, or `pyproject.toml` manually to add dependencies. Use `pnpm add <pkg>` or `uv add <pkg>`.
3. **Strict Typing**: Standard typing notations are mandatory in both TypeScript and Python. `any` is forbidden.
4. **Conventional Commits**: Commit messages must be concise, single-line only (e.g., `feat(auth): add student domain validation`).
5. **Feature Branching & Integration to Main**: Every significant change, feature, or non-trivial bug fix must be grouped and developed within a dedicated branch (e.g., `feat/<name>`, `fix/<name>`), thoroughly tested, and integrated (merged) into `main` upon completion.
6. **Brand Name**: Always format as `BuscaTuNido` (PascalCase, single word).
7. **Strict Prohibition of Hardcoded Values & Seed-First Rule**: Hardcoded values, dummy/mock data, synthetic fallbacks, or arbitrary magic numbers/strings are strictly forbidden across both `api` and `web` unless explicitly requested by the user. If initial, sample, or test data is required, it must be created in the corresponding seed file (e.g., `api/prisma/seed.ts`, `seed-utils.ts`) or dedicated fixture file. Always connect to real APIs, database sources, or display clean empty states.
8. **Ephemeral Verification & Incremental Caches**: Never run persistent background daemons (`--watch`) in agent or worker execution routines. All verification checks must be one-shot and terminate cleanly. Always preserve `.tsbuildinfo` incremental caches to guarantee sub-6s type verification.
