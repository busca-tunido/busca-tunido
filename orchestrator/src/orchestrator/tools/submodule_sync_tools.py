import subprocess
from pathlib import Path
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel

def sync_monorepo_submodules() -> tuple[bool, str]:
    root_dir = Path(__file__).resolve().parents[4]

    subprocess.run(["git", "add", "web", "api"], cwd=str(root_dir), capture_output=True)

    diff_res = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=str(root_dir),
        capture_output=True,
        text=True,
    )

    if diff_res.returncode != 0:
        return False, f"Failed to check git cached diff in root: {diff_res.stderr.strip()}"

    staged = [line.strip() for line in diff_res.stdout.splitlines() if line.strip()]
    if not any(s in ("web", "api") for s in staged):
        return True, "Root monorepo submodule pointers are already up-to-date."

    commit_res = subprocess.run(
        ["git", "commit", "-m", "chore(submodules): synchronize web and api integration commits"],
        cwd=str(root_dir),
        capture_output=True,
        text=True,
    )

    if commit_res.returncode != 0:
        return False, f"Failed to commit submodule pointer update: {commit_res.stderr.strip()}"

    return True, "Successfully updated and committed monorepo submodule pointers."

class SyncSubmodulesInput(BaseModel):
    pass

class SyncSubmodulesTool(BaseTool):
    name: str = "sync_submodule_pointers"
    description: str = "Stages and commits updated git submodule pointers for web and api in the root monorepo."
    args_schema: Type[BaseModel] = SyncSubmodulesInput

    def _run(self) -> str:
        passed, msg = sync_monorepo_submodules()
        return msg
