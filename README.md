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

Ensure the following tools and runtimes are installed in your development environment:

#### 1. Runtimes & Package Managers

- **Node.js** >= 20.x
- **pnpm** >= 9.x
- **Python** >= 3.12
- **uv** >= 0.4.x

#### 2. Multi-Agent Orchestration & CLI Tools

- **Worktrunk (`wt`)**: Parallel Git worktree manager used by the CrewAI orchestrator to provision isolated agent worktrees (`cargo install worktrunk` or binary from [worktrunk.dev](https://worktrunk.dev)).
- **Antigravity CLI (`agy`)**: Command-line autonomous agent runner used by the orchestrator to execute worker tasks (`agy --version`).

#### 3. Database & System Utilities (Backend)

- **PostgreSQL CLI** (`initdb`, `pg_ctl`, `pg_isready` in PATH for local cluster management, or cloud PostgreSQL connection).

#### Verify Prerequisites

```bash
git --version
node -v
pnpm -v
uv --version
wt --version
agy --version
```

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

  # Verify quality gate across both web and api submodules
  uv run python main.py verify --target both

  # List all multi-agent waves and target files
  uv run python main.py list-waves

  # Run a specific wave or range of waves
  uv run python main.py run-wave 3
  uv run python main.py run-waves --start 1 --end 5
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
