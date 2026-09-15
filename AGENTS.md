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
├── orchestrator/                         # CrewAI multi-agent orchestrator (Python + uv)
├── README.md                             # Minimal project overview
└── AGENTS.md                             # Monorepo agent rules and guidelines
```

---

## 2. Token-Efficient Parallel Agent Architecture

To prevent token waste, context pollution, and compilation conflicts across concurrent agents, development follows strict role segregation:

### Two-Tier Agent Model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 CREWAI ORCHESTRATOR & INTEGRATOR ("Head of All")            │
│  - Plans DAG waves with disjoint file sets.                                 │
│  - Provisions isolated Git worktrees per task.                             │
│  - Dispatches Worker agents via lean agy commands.                          │
│  - Merges worker branches into base integration branches.                   │
│  - Connects shared hubs (app.module.ts, layout.tsx).                        │
│  - Runs centralized quality gates: Biome autofix, TSC, Tests, Builds.       │
│  - Manages compiler diagnostics as a central error work queue.              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
              ┌───────────────────────┴───────────────────────┐
              ▼                                               ▼
┌───────────────────────────┐                   ┌───────────────────────────┐
│     WORKER AGENT (A)      │                   │     WORKER AGENT (B)      │
│ - Implements pure code    │                   │ - Implements pure code    │
│   in exclusive files.     │                   │   in exclusive files.     │
│ - Strict typing notations.│                   │ - Strict typing notations.│
│ - FORBIDDEN: pnpm build,  │                   │ - FORBIDDEN: pnpm build,  │
│   tsc, biome, git stash,  │                   │   tsc, biome, git stash,  │
│   git reset, slow tools.  │                   │   git reset, slow tools.  │
│ - git add <files>         │                   │ - git add <files>         │
│ - Conventional commit (1L)│                   │ - Conventional commit (1L)│
│ - Exits immediately.      │                   │ - Exits immediately.      │
└───────────────────────────┘                   └───────────────────────────┘
```

### Critical Worker Rules:

1. **No Slow Commands**: Workers MUST NOT execute `pnpm build`, `tsc`, `nest build`, `biome check`, or `git stash`. These commands pollute the context window with thousands of terminal tokens.
2. **Pure Implementation**: Workers focus exclusively on writing strictly-typed code for their designated files.
3. **Targeted Staging**: Workers only run `git add <file1> <file2>`, followed by a single-line conventional commit.

### Orchestrator / Integrator Quality Gate:

The Orchestrator runs all checks centrally on the merged integration branch in one pass:

1. `pnpm run check`: Global Biome formatting and auto-fixing in milliseconds.
2. `pnpm exec tsc --noEmit` / `nest build`: Static type verification.
3. `pnpm run review`: Verification exit-code check.
4. `pnpm vitest run`: Unit tests.

---

## 3. Worktree Management with Worktrunk (`wt`)

All parallel worktrees are managed using **Worktrunk** (`wt` CLI):

- **Create**: `wt -C <web|api> switch --create <branch-name>`
- **Inspect**: `wt -C <web|api> list`
- **Integrate / Merge**: `wt -C <web|api> merge <branch-name>`
- **Teardown**: `wt -C <web|api> remove <branch-name> -y -D`

CrewAI tools in `orchestrator/src/orchestrator/tools/git_worktree_tools.py` wrap `wt` directly to guarantee deterministic worktree isolation and cleanup.

---

## 4. General Development Constraints

1. **No Code Comments**: Do not write comments inside code unless explicitly requested by the user. Use descriptive naming and explicit types instead.
2. **No Direct Config Edits**: Never modify `package.json`, `pnpm-lock.yaml`, or `pyproject.toml` manually to add dependencies. Use `pnpm add <pkg>` or `uv add <pkg>`.
3. **Strict Typing**: Standard typing notations are mandatory in both TypeScript and Python. `any` is forbidden.
4. **Conventional Commits**: Commit messages must be concise, single-line only (e.g., `feat(auth): add student domain validation`).
5. **Brand Name**: Always format as `BuscaTuNido` (PascalCase, single word).
