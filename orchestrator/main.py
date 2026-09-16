import sys
from pathlib import Path

src_dir = str(Path(__file__).resolve().parent / "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

import click
from orchestrator.tools.verification_tools import RunQualityGateTool
from orchestrator.tools.git_worktree_tools import ListWorktreesTool
from orchestrator.crew import BuscaTunidoCrew
from orchestrator.waves import WaveRunner, WAVES

@click.group()
def cli() -> None:
    pass

@cli.command()
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

@cli.command()
@click.option("--repo", type=click.Choice(["web", "api"]), default="web", help="Target repository")
def worktrees(repo: str) -> None:
    tool = ListWorktreesTool()
    click.echo(tool.run(repo=repo))

@cli.command(name="list-waves")
def list_waves() -> None:
    click.echo("=== ONDAS DEFINIDAS EN BUSCA-TUNIDO ===")
    for wave_num, wave in sorted(WAVES.items()):
        click.echo(f"\n[Onda {wave_num}] {wave.description}")
        for task in wave.tasks:
            click.echo(f"  - {task.task_id} [{task.repo}]: {task.branch_name}")
            click.echo(f"    Archivos: {', '.join(task.target_files)}")
            click.echo(f"    Commit: {task.commit_message}")

@cli.command(name="run-wave")
@click.argument("wave_number", type=int)
@click.option("--dry-run", is_flag=True, help="Preview wave plan without modifying repositories")
def run_wave(wave_number: int, dry_run: bool) -> None:
    runner = WaveRunner()
    result = runner.run_wave(wave_number=wave_number, dry_run=dry_run)
    click.echo(result)

@cli.command()
@click.option("--requirement", "-r", required=True, help="Feature or bug requirement to plan")
def plan(requirement: str) -> None:
    crew = BuscaTunidoCrew()
    result = crew.run_planning(requirement)
    click.echo(result)

@cli.command()
@click.option("--repo", type=click.Choice(["web", "api"]), required=True, help="Target repository")
@click.option("--branches", "-b", multiple=True, required=True, help="Branches to merge")
@click.option("--worktrees", "-w", multiple=True, required=True, help="Worktrees to prune")
def integrate(repo: str, branches: tuple[str, ...], worktrees: tuple[str, ...]) -> None:
    crew = BuscaTunidoCrew()
    result = crew.run_integration(repo, list(branches), list(worktrees))
    click.echo(result)

if __name__ == "__main__":
    cli()
