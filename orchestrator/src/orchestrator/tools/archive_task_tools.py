import re
import shutil
import subprocess
from pathlib import Path
from typing import Literal, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

def get_highest_completed_index(completed_dir: Path) -> int:
    if not completed_dir.exists():
        return 0
    indices: list[int] = []
    for file in completed_dir.glob("*.md"):
        match = re.match(r"^(\d{3})[-_]", file.name)
        if match:
            indices.append(int(match.group(1)))
    return max(indices) if indices else 0

def archive_task_file(repo: Literal["web", "api"], task_file_rel: str) -> tuple[bool, str]:
    base_dir = Path(__file__).resolve().parents[4]
    repo_dir = base_dir / repo
    tasks_dir = repo_dir / "tasks"
    completed_dir = tasks_dir / "completed"
    completed_dir.mkdir(parents=True, exist_ok=True)

    file_name = Path(task_file_rel).name
    source_file = tasks_dir / file_name
    if not source_file.exists():
        return False, f"Source task file not found: {source_file}"

    next_idx = get_highest_completed_index(completed_dir) + 1
    dest_name = f"{next_idx:03d}_{file_name}"
    dest_file = completed_dir / dest_name

    shutil.move(str(source_file), str(dest_file))

    subprocess.run(["git", "add", str(source_file), str(dest_file)], cwd=str(repo_dir), capture_output=True)
    commit_msg = f"chore(tasks): archive completed task {dest_name.replace('.md', '')}"
    subprocess.run(["git", "commit", "-m", commit_msg], cwd=str(repo_dir), capture_output=True)

    return True, f"Successfully archived {file_name} -> {dest_name}"

class ArchiveTaskInput(BaseModel):
    repo: Literal["web", "api"] = Field(description="Target repository: 'web' or 'api'")
    task_files: list[str] = Field(description="List of task file names or relative paths in tasks/ to archive")

class ArchiveCompletedTasksTool(BaseTool):
    name: str = "archive_completed_tasks"
    description: str = "Moves verified and merged task specifications from tasks/ to tasks/completed/ with sequential numbering."
    args_schema: Type[BaseModel] = ArchiveTaskInput

    def _run(self, repo: Literal["web", "api"], task_files: list[str]) -> str:
        results: list[str] = []
        for tf in task_files:
            ok, msg = archive_task_file(repo, tf)
            results.append(msg)
        return "\n".join(results)
