import re
from dataclasses import dataclass, field
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
    depends_on: list[str] = field(default_factory=list)

def normalize_file_name(name: str) -> str:
    return name.strip().replace("\\", "/").lstrip("./")

def compute_dag_waves(tasks: list[DiscoveredTask]) -> dict[int, list[DiscoveredTask]]:
    if not tasks:
        return {}

    task_map = {t.task_id: t for t in tasks}
    for t in tasks:
        file_stem = Path(t.task_file).stem
        task_map[file_stem] = t
        task_map[t.task_file] = t

    initial_waves: dict[int, list[DiscoveredTask]] = {}
    for t in tasks:
        max_dep_wave = 0
        for dep in t.depends_on:
            dep_clean = dep.replace(".md", "").strip()
            if dep_clean in task_map:
                dep_task = task_map[dep_clean]
                max_dep_wave = max(max_dep_wave, dep_task.wave_number)
        effective_wave = max(t.wave_number, max_dep_wave + 1 if max_dep_wave > 0 else t.wave_number)
        t.wave_number = effective_wave
        initial_waves.setdefault(effective_wave, []).append(t)

    sorted_wave_nums = sorted(initial_waves.keys())
    final_waves: dict[int, list[DiscoveredTask]] = {}

    current_wave_num = 1
    for w_num in sorted_wave_nums:
        wave_tasks = initial_waves[w_num]
        buckets: list[list[DiscoveredTask]] = []
        bucket_files: list[set[str]] = []

        for task in wave_tasks:
            task_files = {normalize_file_name(f) for f in task.target_files}
            placed = False
            for idx, existing_files in enumerate(bucket_files):
                if existing_files.isdisjoint(task_files) or not task_files:
                    buckets[idx].append(task)
                    bucket_files[idx].update(task_files)
                    placed = True
                    break

            if not placed:
                buckets.append([task])
                bucket_files.append(set(task_files))

        for bucket in buckets:
            for t in bucket:
                t.wave_number = current_wave_num
            final_waves[current_wave_num] = bucket
            current_wave_num += 1

    return final_waves

def parse_task_file(repo: Literal["web", "api"], file_path: Path) -> DiscoveredTask:
    content = file_path.read_text(encoding="utf-8")
    stem = file_path.stem

    wave_match = re.search(r"Wave\s*(\d+)", content, re.IGNORECASE)
    wave_number = int(wave_match.group(1)) if wave_match else 1

    id_match = re.search(r"\b(WEB-\d+|API-\d+)\b", content)
    task_id = id_match.group(1) if id_match else f"{repo.upper()}-{stem}"
    branch_name = f"feat/{stem}"

    depends_on: list[str] = []
    dep_match = re.search(r"Dependencies.*:\s*\[(.*?)\]", content, re.IGNORECASE)
    if dep_match:
        deps_raw = dep_match.group(1).split(",")
        depends_on = [d.strip().strip("'\"`") for d in deps_raw if d.strip()]

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
    commit_message = commit_match.group(1) if commit_match else f"feat({repo}): implement {stem.replace('-', ' ')}"
    rel_path = f"tasks/{file_path.name}"

    return DiscoveredTask(
        task_id=task_id,
        repo=repo,
        task_file=rel_path,
        wave_number=wave_number,
        branch_name=branch_name,
        target_files=target_files,
        commit_message=commit_message,
        depends_on=depends_on,
    )

def get_discovered_tasks(repo: Literal["web", "api", "both"] = "both") -> list[DiscoveredTask]:
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
            task = parse_task_file(r, file_path)
            discovered.append(task)
    return discovered

def get_disjoint_waves(repo: Literal["web", "api", "both"] = "both") -> dict[int, list[DiscoveredTask]]:
    tasks = get_discovered_tasks(repo)
    return compute_dag_waves(tasks)

class DiscoverTasksInput(BaseModel):
    repo: Literal["web", "api", "both"] = Field(
        default="both",
        description="Target repository to scan for pending tasks: 'web', 'api', or 'both'",
    )

class DiscoverPendingTasksTool(BaseTool):
    name: str = "discover_pending_tasks"
    description: str = "Scans web/tasks and api/tasks to discover pending markdown specifications and their target files."
    args_schema: Type[BaseModel] = DiscoverTasksInput

    def _run(self, repo: Literal["web", "api", "both"] = "both") -> str:
        waves = get_disjoint_waves(repo)
        if not waves:
            return "No pending task specifications found in active tasks directories."

        total_tasks = sum(len(ts) for ts in waves.values())
        lines: list[str] = [f"Found {total_tasks} pending task specification(s) grouped into {len(waves)} DAG wave(s):"]

        for w_num in sorted(waves.keys()):
            lines.append(f"\n[Wave {w_num}]")
            for task in waves[w_num]:
                files_str = ", ".join(task.target_files) if task.target_files else "None specified"
                deps_str = ", ".join(task.depends_on) if task.depends_on else "None"
                lines.append(f"  - {task.task_id} [{task.repo}]: {task.branch_name}")
                lines.append(f"    File: {task.task_file}")
                lines.append(f"    Target Files: {files_str}")
                lines.append(f"    Depends on: {deps_str}")
                lines.append(f"    Commit: {task.commit_message}")

        return "\n".join(lines)
