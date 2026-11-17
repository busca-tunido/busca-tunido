# Context & Architectural Guidelines for AI Coding Assistants (BuscaTuNido Monorepo)

This document establishes high-level monorepo conventions, shared development constraints, and the opt-in multi-agent task orchestration methodology for **BuscaTuNido**.

---

## 1. Monorepo Structure & Submodules

The workspace manages two Git submodules alongside a shared task runner and a multi-agent orchestration engine:

```text
busca-tunido/
├── .gitmodules        # Git submodule configuration
├── web/               # Next.js frontend (submodule)
├── api/               # NestJS + Prisma backend (submodule)
├── orchestrator/      # CrewAI multi-agent orchestrator (Python + uv)
├── justfile           # Root task runner (just)
├── README.md          # Project overview
└── AGENTS.md          # Monorepo agent rules and guidelines
```

---

## 2. Opt-In Task-Driven Methodology & Orchestrator (`tasks/[task-name].md`)

> [!IMPORTANT]
> **Explicit-Request-Only Clause (Opt-In Methodology)**:
> The task-driven (`tasks/[task-name].md`) DAG wave planning and multi-agent orchestrator workflow described in this section **MUST ONLY be used when explicitly requested by the user**.
> For standard development requests, bug fixes, or feature work without an explicit request for `tasks/` orchestration, work directly in the target repository (`api` or `web`) following standard feature-branching and quality-gate rules—do **not** create `tasks/*.md` files or spin up parallel worktree waves automatically.

### Task-Driven Lifecycle (`web/tasks/` & `api/tasks/`):

1. **Task Breakdown by Purpose & Topology**:
   - Decompose user requirements into structured `tasks/[task-name].md` files inside the corresponding submodule (`web/tasks/` or `api/tasks/`), omitting any numeric index prefix while active.
   - Assign each task an `Execution Profile` (Wave, Mode, Role, Dependencies, Collision Risk) and explicit `## Target Files`.
2. **Review & Clarification Gate**:
   - Present the generated DAG and execution waves to the user for review and approval before executing waves.
3. **Parallel Decomposition & Disjoint File Sets Rule**:
   - Tasks with disjoint target files ($Files(Task\_A) \cap Files(Task\_B) = \emptyset$) can run in `PARALLEL` within the same wave.
   - Tasks touching overlapping files or shared integration hubs (schemas, root modules, global layouts/providers, lockfiles) must be sequenced across waves or deferred to the integration gate.

> [!IMPORTANT]
> **Task Naming & Archiving Convention**:
> - **Active tasks MUST NOT use numeric prefixes**: Name active tasks in `tasks/` using descriptive kebab-case without numbers (e.g., `tasks/some-feature.md`).
> - **Sequential numbering is strictly reserved for `tasks/completed/`**: A three-digit sequential index (`001_`, `002_`, etc.) is assigned **only** when a task is completed, verified, merged, and archived into `tasks/completed/`.

### Standard `[task-name].md` Structure:

- `# Task: [Descriptive Title]`
- `## Execution Profile`: Wave/Batch, Execution Mode (`PARALLEL` | `SEQUENTIAL`), Assigned Role (`Worker Agent` | `Integrator Agent`), Dependencies (`depends_on`), Collision Risk.
- `## Target Files`: `Exclusive` and `Shared / Integration Points`.
- `## Objective`, `## Technical Specifications`, `## Checklist`, and `## Verification`.

### Agent Roles & Quality Gate (When Orchestrated):

- **Worker Agent**: Operates in an isolated branch/worktree under `trees/`, modifies only its assigned exclusive files, skips heavy local build/check commands to stay token-efficient, and creates a single-line conventional commit.
- **Integrator Agent**: Operates on the integration branch, merges worker branches, reconciles shared hubs, runs the centralized quality gate (Biome check/review, incremental TypeScript check, Vitest), archives completed task files, and cleans up temporary worktrees.

---

## 3. Orchestrator & Worktree Tooling (`orchestrator/` & `just`)

When the opt-in orchestration workflow is requested:

- **Orchestrator Engine**: `orchestrator/` implements a CrewAI Flow + Crew + Skills architecture backed by the Antigravity CLI (`agy`) and Worktrunk (`wt`).
- **Worktree Isolation**: Parallel worktrees are isolated inside the git-ignored `trees/` directory using `orchestrator/config/wt.toml`.
- **Root Commands (`just`)**:
  - `just install`: Initialize submodules and install dependencies in `web` and `api`.
  - `just check [target]`, `just typecheck [target]`, `just test [target]`: Run Biome, TypeScript, and Vitest across `web`, `api`, or `both`.
  - `just openapi`: Build `api`, export OpenAPI schema, and regenerate `web` client types.
  - `just seed`: Seed the database via `api`.
  - `just discover`, `just plan`, `just run-flow`, `just verify`, `just new-task`, `just archive`: Drive the `orchestrator/` CLI when executing the opt-in task workflow.

---

## 4. General Development Constraints

1. **No Code Comments**: Do not write comments inside code unless explicitly requested by the user. Use descriptive naming and explicit types instead.
2. **No Direct Config Edits**: Never modify `package.json`, `pnpm-lock.yaml`, or `pyproject.toml` manually to add dependencies. Use `pnpm add <pkg>` or `uv add <pkg>`.
3. **Strict Typing**: Standard typing notations are mandatory in both TypeScript and Python. `interface` and `any` are forbidden in TypeScript (`type` aliases only).
4. **Conventional Commits**: Commit messages must be concise, single-line only (e.g., `feat(auth): add student domain validation`).
5. **Feature Branching & Integration to Main**: Every significant change, feature, or non-trivial bug fix must be developed within a dedicated branch (e.g., `feat/<name>`, `fix/<name>`), thoroughly tested, and merged cleanly into `main` upon completion.
6. **Brand Name**: Always format as `BuscaTuNido` (PascalCase, single word).
7. **Strict Prohibition of Hardcoded Values & Seed-First Rule**: Hardcoded values, dummy/mock data, synthetic fallbacks, or arbitrary magic numbers/strings are strictly prohibited across both `api` and `web` unless explicitly requested by the user. Initial, sample, or test data must live in `api/scripts/seeds/` or dedicated test fixtures. Always connect to real APIs, database sources, or display clean empty states.
8. **Ephemeral Verification & Incremental Caches**: Never run persistent background daemons (`--watch`) in agent verification routines. All verification checks must be one-shot and terminate cleanly. Preserve `.tsbuildinfo` incremental caches.
9. **100% OpenAPI Parity & Backend-First Contract Rule**: The backend API must maintain 100% OpenAPI documentation completeness across all endpoints and DTOs. The frontend must exclusively consume types generated from OpenAPI via `just openapi`; manual reimplementation of backend types and synthetic fallbacks are strictly prohibited. Any new field or capability must first be implemented in the backend before being consumed in the frontend.
