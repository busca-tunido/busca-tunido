import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

@dataclass
class DiscoveredTask:
    task_id: str
    repo: Literal["web", "api"]
    task_file: str
    wave_number: int
    branch_name: str
    target_files: list[str]
    commit_message: str

class DiscoverTasksInput(BaseModel):
    repo: Literal["web", "api", "both"] = Field(
        default="both",
        description="Target repository to scan for pending tasks: 'web', 'api', or 'both'",
    )

class DiscoverPendingTasksTool(BaseTool):
    name: str = "discover_pending_tasks"
    description: str = "Scans web/tasks and api/tasks to discover pending markdown specifications and their target files."
    args_schema: Type[BaseModel] = DiscoverTasksInput

    def _parse_task_file(self, repo: Literal["web", "api"], file_path: Path) -> DiscoveredTask:
        content = file_path.read_text(encoding="utf-8")
        stem = file_path.stem

        wave_match = re.search(r"Wave\s*(\d+)", content, re.IGNORECASE)
        wave_number = int(wave_match.group(1)) if wave_match else 1

        id_match = re.search(r"\b(WEB-\d+|API-\d+)\b", content)
        if id_match:
            task_id = id_match.group(1)
        else:
            task_id = f"{repo.upper()}-{stem}"

        branch_name = f"feat/{stem}"

        target_files: list[str] = []
        in_target_files = False
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("## Target Files"):
                in_target_files = True
                continue
            if in_target_files and stripped.startswith("## "):
                in_target_files = False
                break
            if in_target_files:
                file_match = re.search(r"[-*]\s*`?([^`\s]+(?:\.tsx|\.ts|\.json|\.css|\.prisma))`?", stripped)
                if file_match:
                    target_files.append(file_match.group(1))

        commit_match = re.search(r"commit with:?\s*['\"]([^'\"]+)['\"]", content, re.IGNORECASE)
        if commit_match:
            commit_message = commit_match.group(1)
        else:
            commit_message = f"feat({repo}): implement {stem.replace('-', ' ')}"

        rel_path = f"tasks/{file_path.name}"
        return DiscoveredTask(
            task_id=task_id,
            repo=repo,
            task_file=rel_path,
            wave_number=wave_number,
            branch_name=branch_name,
            target_files=target_files,
            commit_message=commit_message,
        )

    def _run(self, repo: Literal["web", "api", "both"] = "both") -> str:
        base_dir = Path(__file__).resolve().parents[4]
        targets: list[Literal["web", "api"]] = ["web", "api"] if repo == "both" else [repo]

        discovered: list[DiscoveredTask] = []
        for r in targets:
            tasks_dir = base_dir / r / "tasks"
            if not tasks_dir.exists():
                continue
            for file_path in sorted(tasks_dir.glob("*.md")):
                if file_path.name.lower() == "readme.md":
                    continue
                task = self._parse_task_file(r, file_path)
                discovered.append(task)

        if not discovered:
            return "No pending task specifications found in active tasks directories."

        lines: list[str] = [f"Found {len(discovered)} pending task specification(s):"]
        waves: dict[int, list[DiscoveredTask]] = {}
        for t in discovered:
            waves.setdefault(t.wave_number, []).append(t)

        for w_num in sorted(waves.keys()):
            lines.append(f"\n[Wave {w_num}]")
            for task in waves[w_num]:
                files_str = ", ".join(task.target_files) if task.target_files else "None specified"
                lines.append(f"  - {task.task_id} [{task.repo}]: {task.branch_name}")
                lines.append(f"    File: {task.task_file}")
                lines.append(f"    Target Files: {files_str}")
                lines.append(f"    Commit: {task.commit_message}")

        return "\n".join(lines)
