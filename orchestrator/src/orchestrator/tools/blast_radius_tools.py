import subprocess
from pathlib import Path
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

def normalize_path(path_str: str) -> str:
    return path_str.strip().replace("\\", "/").lstrip("./")

def check_worktree_blast_radius(
    worktree_path: str | Path,
    allowed_files: list[str],
) -> tuple[bool, list[str], str]:
    wt_path = Path(worktree_path).resolve()
    if not wt_path.exists():
        return False, [], f"Worktree path does not exist: {wt_path}"

    res = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(wt_path),
        capture_output=True,
        text=True,
    )

    diff_head = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1..HEAD"],
        cwd=str(wt_path),
        capture_output=True,
        text=True,
    )

    touched_files: set[str] = set()

    if res.returncode == 0 and res.stdout.strip():
        for line in res.stdout.splitlines():
            line = line.strip()
            if len(line) > 3:
                file_rel = line[3:].strip()
                if " -> " in file_rel:
                    file_rel = file_rel.split(" -> ")[1].strip()
                touched_files.add(normalize_path(file_rel))

    if diff_head.returncode == 0 and diff_head.stdout.strip():
        for line in diff_head.stdout.splitlines():
            if line.strip():
                touched_files.add(normalize_path(line.strip()))

    ignored_patterns = {
        "tsconfig.tsbuildinfo",
        ".next",
        "dist",
        "node_modules",
    }

    normalized_allowed = {normalize_path(f) for f in allowed_files}

    rogue_files: list[str] = []
    for touched in touched_files:
        if any(ignored in touched for ignored in ignored_patterns):
            continue

        matched = False
        for allowed in normalized_allowed:
            if touched == allowed or touched.endswith(allowed) or allowed.endswith(touched):
                matched = True
                break

        if not matched:
            rogue_files.append(touched)

    if rogue_files:
        report = (
            f"Blast radius violation detected in {wt_path.name}!\n"
            f"The following files were modified outside the exclusive target files:\n"
            + "\n".join(f"  - {f}" for f in rogue_files)
        )
        return False, rogue_files, report

    return True, [], "Blast radius check passed cleanly. Only permitted target files were modified."

class BlastRadiusInput(BaseModel):
    worktree_path: str = Field(description="Path to the worker's git worktree")
    allowed_files: list[str] = Field(description="Exclusive target files allowed for this task")

class ValidateBlastRadiusTool(BaseTool):
    name: str = "validate_blast_radius"
    description: str = "Validates that a worker did not touch or modify any files outside its designated target files."
    args_schema: Type[BaseModel] = BlastRadiusInput

    def _run(self, worktree_path: str, allowed_files: list[str]) -> str:
        passed, rogue_files, report = check_worktree_blast_radius(worktree_path, allowed_files)
        return report
