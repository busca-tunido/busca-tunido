import json
import shutil
import subprocess
from pathlib import Path
from typing import Literal, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

def get_wt_bin() -> str:
    return shutil.which("wt.exe") or shutil.which("wt") or "wt"

class CreateWorktreeInput(BaseModel):
    repo: Literal["web", "api"] = Field(description="Target repository: 'web' or 'api'")
    branch_name: str = Field(description="New git branch name for the worker")

class CreateWorktreeTool(BaseTool):
    name: str = "create_worktrunk_worktree"
    description: str = "Creates an isolated Git worktree and branch using worktrunk (wt) for a parallel worker agent."
    args_schema: Type[BaseModel] = CreateWorktreeInput

    def _run(self, repo: Literal["web", "api"], branch_name: str) -> str:
        base_dir = Path(__file__).resolve().parents[4]
        repo_dir = base_dir / repo

        wt_bin = get_wt_bin()
        subprocess.run([wt_bin, "-C", str(repo_dir), "remove", "--force", branch_name, "-D"], capture_output=True, text=True)
        cmd = [wt_bin, "-C", str(repo_dir), "switch", "--create", branch_name]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            return f"Failed to create worktree with wt: {res.stderr.strip() or res.stdout.strip()}"

        list_cmd = [wt_bin, "-C", str(repo_dir), "list", "--format", "json"]
        list_res = subprocess.run(list_cmd, capture_output=True, text=True)
        worktree_path = ""
        if list_res.returncode == 0:
            try:
                data = json.loads(list_res.stdout)
                for item in data.get("items", []):
                    if item.get("branch") == branch_name:
                        worktree_path = item.get("worktree", {}).get("path", "")
                        break
            except json.JSONDecodeError:
                pass

        if not worktree_path:
            worktree_path = str(base_dir / f"{repo}.{branch_name}")

        return f"Successfully created worktree for branch '{branch_name}' at: {worktree_path}"

class MergeWorktreeInput(BaseModel):
    repo: Literal["web", "api"] = Field(description="Target repository: 'web' or 'api'")
    branch_name: str = Field(description="Branch name to merge into main")

class MergeWorktreeTool(BaseTool):
    name: str = "merge_worktrunk_branch"
    description: str = "Merges a completed worker branch into main using worktrunk (wt)."
    args_schema: Type[BaseModel] = MergeWorktreeInput

    def _run(self, repo: Literal["web", "api"], branch_name: str) -> str:
        base_dir = Path(__file__).resolve().parents[4]
        repo_dir = base_dir / repo

        cmd = ["git", "-C", str(repo_dir), "merge", "--no-ff", "-m", f"merge({repo}): integrate {branch_name}", branch_name]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            return f"Failed to merge {branch_name}: {res.stderr.strip() or res.stdout.strip()}"

        return f"Successfully merged branch '{branch_name}' into {repo}/main"

class RemoveWorktreeInput(BaseModel):
    repo: Literal["web", "api"] = Field(description="Target repository: 'web' or 'api'")
    branch_name: str = Field(description="Branch/worktree name to remove")

class RemoveWorktreeTool(BaseTool):
    name: str = "remove_worktrunk_worktree"
    description: str = "Removes a worktree and deletes its branch using worktrunk (wt)."
    args_schema: Type[BaseModel] = RemoveWorktreeInput

    def _run(self, repo: Literal["web", "api"], branch_name: str) -> str:
        base_dir = Path(__file__).resolve().parents[4]
        repo_dir = base_dir / repo

        wt_bin = get_wt_bin()
        cmd = [wt_bin, "-C", str(repo_dir), "remove", "--force", branch_name, "-D"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            return f"Failed to remove worktree {branch_name} with wt: {res.stderr.strip() or res.stdout.strip()}"

        return f"Successfully removed worktree and branch '{branch_name}' via worktrunk."

class ListWorktreesInput(BaseModel):
    repo: Literal["web", "api"] = Field(description="Target repository: 'web' or 'api'")

class ListWorktreesTool(BaseTool):
    name: str = "list_worktrunk_worktrees"
    description: str = "Lists active worktrees and their status using worktrunk (wt)."
    args_schema: Type[BaseModel] = ListWorktreesInput

    def _run(self, repo: Literal["web", "api"]) -> str:
        base_dir = Path(__file__).resolve().parents[4]
        repo_dir = base_dir / repo

        wt_bin = get_wt_bin()
        cmd = [wt_bin, "-C", str(repo_dir), "list"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            return f"Failed to list worktrees with wt: {res.stderr.strip()}"

        return res.stdout.strip()
