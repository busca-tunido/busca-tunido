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

### Clone with Submodules

```bash
git clone --recurse-submodules https://github.com/busca-tunido/busca-tunido.git
```

If already cloned without submodules:

```bash
git submodule update --init --recursive
```

### Quick Commands

- **Web Frontend**:
  ```bash
  cd web
  pnpm install
  pnpm dev
  ```

- **Backend API**:
  ```bash
  cd api
  pnpm install
  pnpm run db:start
  pnpm start:dev
  ```

- **CrewAI Orchestrator**:
  ```bash
  cd orchestrator
  uv run python main.py verify --target both
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

