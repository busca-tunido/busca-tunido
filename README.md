# BuscaTuNido

Monorepository and multi-agent orchestration workspace for the BuscaTuNido student accommodation platform.

## Architecture

```
busca-tunido/
├── web/           # Frontend Next.js application (Git submodule)
├── api/           # Backend NestJS REST API (Git submodule)
└── orchestrator/  # Multi-agent orchestration engine (CrewAI & uv)
```

## Public Deployments & Links

- **Official Web App**: [https://buscatunido.vercel.app](https://buscatunido.vercel.app)
- **Production API**: [https://buscatunido-api.onrender.com](https://buscatunido-api.onrender.com)
- **API Documentation**: [https://buscatunido-api.onrender.com/api/docs](https://buscatunido-api.onrender.com/api/docs)

## Submodules

- **Web Repository**: [https://github.com/busca-tunido/web.git](https://github.com/busca-tunido/web.git)
- **API Repository**: [https://github.com/busca-tunido/api.git](https://github.com/busca-tunido/api.git)

## Getting Started

### Prerequisites

- **Node.js** >= 20.x
- **pnpm** >= 9.x
- **Python** >= 3.12
- **uv** >= 0.4.x
- **just**: Command runner
- **Worktrunk (`wt`)**: Git worktree manager.
- **Antigravity CLI (`agy`)**
- **PostgreSQL CLI**

### Clone with Submodules

```bash
git clone --recurse-submodules https://github.com/busca-tunido/busca-tunido.git
# If already cloned without submodules:
git submodule update --init --recursive
```

### Quick Commands

All common tasks can be run directly from the root using [just](https://github.com/casey/just):

```bash
# Install dependencies across all submodules
just install

# Development servers
just web-dev              # Start Next.js frontend (Turbopack)
just api-db               # Start local PostgreSQL cluster daemon
just api-dev              # Start NestJS backend in watch mode

# Multi-Agent Orchestrator
just verify               # Quality gate (Biome, TSC, Vitest) across both web and api
just waves                # List all multi-agent waves and assigned files
just run-wave 3           # Execute a specific wave in parallel worktrees
just run-waves 1 5        # Run a range of waves sequentially
```

### Parallel Worktree Management (Worktrunk)

Parallel agent workspaces are managed using [Worktrunk](https://worktrunk.dev) (`wt`):

```bash
# Create worktree and branch for a worker
wt -C web switch --create feat/task-name

# List active worktrees and status
wt -C web list

# Remove worktree and delete branch after integration
wt -C web remove feat/task-name -y -D
```
