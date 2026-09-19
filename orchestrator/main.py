import sys
from pathlib import Path

src_dir = str(Path(__file__).resolve().parent / "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

import click
from orchestrator.crew import BuscaTunidoCrew
from orchestrator.flow import BuscaTunidoFlow
from orchestrator.tools.git_worktree_tools import ListWorktreesTool
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
