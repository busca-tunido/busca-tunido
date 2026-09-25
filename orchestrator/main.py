import sys
from pathlib import Path

src_dir = str(Path(__file__).resolve().parent / "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

import click
from orchestrator.crew import BuscaTunidoCrew
from orchestrator.flow import BuscaTunidoFlow
from orchestrator.tools.archive_task_tools import archive_task_file
from orchestrator.tools.git_worktree_tools import ListWorktreesTool
from orchestrator.tools.self_healing_tools import attempt_quality_gate_healing
from orchestrator.tools.submodule_sync_tools import sync_monorepo_submodules
from orchestrator.tools.task_discovery_tools import DiscoverPendingTasksTool
from orchestrator.tools.verification_tools import RunQualityGateTool

@click.group()
def cli() -> None:
    pass

@cli.command(name="run-flow")
def run_flow() -> None:
    click.echo("=== INICIANDO BUSCA-TUNIDO CANONICAL CREWAI FLOW ===")
    flow = BuscaTunidoFlow()
    result = flow.kickoff()
    click.echo("\n=== RESULTADO DEL FLOW ===")
    click.echo(result)

@cli.command(name="discover")
@click.option(
    "--repo",
    type=click.Choice(["web", "api", "both"]),
    default="both",
    help="Target repository to scan",
)
def discover(repo: str) -> None:
    tool = DiscoverPendingTasksTool()
    click.echo(tool.run(repo=repo))

@cli.command(name="verify")
@click.option(
    "--target",
    type=click.Choice(["web", "api", "both"]),
    default="both",
    help="Target submodule to verify",
)
def verify(target: str) -> None:
    tool = RunQualityGateTool()
    report = tool.run(target=target)
    click.echo(report)

@cli.command(name="heal")
@click.option(
    "--target",
    type=click.Choice(["web", "api", "both"]),
    default="both",
    help="Target submodule to verify and heal",
)
@click.option(
    "--retries",
    type=int,
    default=2,
    help="Maximum self-healing attempts",
)
def heal(target: str, retries: int) -> None:
    click.echo(f"=== EJECUTANDO COMPUERTA DE CALIDAD CON AUTORREPARACIÓN ({target}) ===")
    passed, summary = attempt_quality_gate_healing(target=target, max_retries=retries)
    click.echo(summary)

@cli.command(name="worktrees")
@click.option(
    "--repo",
    type=click.Choice(["web", "api"]),
    default="web",
    help="Target repository",
)
def worktrees(repo: str) -> None:
    tool = ListWorktreesTool()
    click.echo(tool.run(repo=repo))

@cli.command(name="archive")
@click.option(
    "--repo",
    type=click.Choice(["web", "api"]),
    required=True,
    help="Target repository containing the task",
)
@click.option(
    "--task",
    required=True,
    help="Task file name or relative path in tasks/ (e.g., custom-feature.md)",
)
def archive(repo: str, task: str) -> None:
    ok, msg = archive_task_file(repo, task)
    click.echo(msg)

@cli.command(name="sync-submodules")
def sync_submodules() -> None:
    ok, msg = sync_monorepo_submodules()
    click.echo(msg)

@cli.command(name="new-task")
@click.option(
    "--repo",
    type=click.Choice(["web", "api"]),
    required=True,
    help="Target repository for the new task spec",
)
@click.option(
    "--slug",
    required=True,
    help="Kebab-case task filename without numbers (e.g. landlord-pension-form)",
)
@click.option(
    "--title",
    required=True,
    help="Descriptive title of the feature or requirement",
)
@click.option(
    "--wave",
    type=int,
    default=1,
    help="Target DAG wave number",
)
@click.option(
    "--mode",
    type=click.Choice(["PARALLEL", "SEQUENTIAL"]),
    default="PARALLEL",
    help="Execution mode",
)
def new_task(repo: str, slug: str, title: str, wave: int, mode: str) -> None:
    base_dir = Path(__file__).resolve().parents[1]
    repo_dir = base_dir / repo
    tasks_dir = repo_dir / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)

    clean_slug = slug.strip().lower().replace(".md", "").replace(" ", "-")
    task_file = tasks_dir / f"{clean_slug}.md"

    if task_file.exists():
        click.echo(f"Error: Task specification already exists at: {task_file}")
        sys.exit(1)

    template = f"""# Task: {title}

## Execution Profile

- **Wave / Batch**: Wave {wave}
- **Execution Mode**: `{mode}`
- **Assigned Role**: `Worker Agent`
- **Dependencies (`depends_on`)**: None
- **Collision Risk**: `LOW (Isolated files)`

## Target Files

- **Exclusive**:
  - `src/{repo}/example.ts`
- **Shared / Integration Points**:
  - None

## Objective

Implement {title.lower()} following mobile-first design and strict typing.

## Technical Specifications

- Standard strict typing (no any).
- No code comments.
- Follow BuscaTuNido conventions.

## Checklist

- [ ] Implement required components/endpoints.
- [ ] Connect domain types.
- [ ] Conventional single-line commit.

## Verification

- Code Quality (Biome): `pnpm run check && pnpm run review`
- Build & Typecheck: `pnpm exec tsc --noEmit`
"""
    task_file.write_text(template, encoding="utf-8")
    click.echo(f"Created task specification: {task_file}")

@cli.command(name="plan")
@click.option(
    "--requirement",
    "-r",
    required=False,
    help="Optional specific requirement to plan",
)
def plan(requirement: str | None) -> None:
    click.echo("=== EJECUTANDO PLANIFICACIÓN CON BUSCATUNIDOCREW ===")
    discovery_tool = DiscoverPendingTasksTool()
    summary = discovery_tool.run(repo="both")
    crew = BuscaTunidoCrew()
    inputs = {
        "tasks_summary": requirement or summary,
        "task_id": "MANUAL_PLAN",
        "worktree_path": "auto",
        "target_files": "auto",
        "task_instructions": requirement or summary,
        "commit_message": "feat: planned feature",
        "branches": "auto",
        "repo": "both",
        "worktrees": "auto",
    }
    result = crew.crew().kickoff(inputs=inputs)
    click.echo(result)

if __name__ == "__main__":
    cli()
