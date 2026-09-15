import subprocess
from pathlib import Path
from typing import Literal, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class CreateWorktreeInput(BaseModel):
    repo: Literal["web", "api"] = Field(description="Target repository: 'web' or 'api'")
    branch_name: str = Field(description="New git branch name for the worker")
    worktree_name: str = Field(description="Directory name for the new worktree inside trees/")

class CreateWorktreeTool(BaseTool):
    name: str = "create_git_worktree"
    description: str = "Creates an isolated Git worktree and branch for a parallel worker agent."
    args_schema: Type[BaseModel] = CreateWorktreeInput

    def _run(self, repo: Literal["web", "api"], branch_name: str, worktree_name: str) -> str:
        base_dir = Path(__file__).resolve().parents[4]
        repo_dir = base_dir / repo
        trees_dir = base_dir / "trees"
        trees_dir.mkdir(parents=True, exist_ok=True)
        worktree_path = trees_dir / worktree_name

        if worktree_path.exists():
            return f"Error: Worktree path already exists at {worktree_path}"

        cmd = [
            "git",
            "-C",
            str(repo_dir),
            "worktree",
            "add",
            "-b",
            branch_name,
            str(worktree_path),
            "main",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            return f"Failed to create worktree: {res.stderr.strip()}"

        return f"Successfully created worktree at {worktree_path} on branch {branch_name}"

class MergeWorktreeInput(BaseModel):
    repo: Literal["web", "api"] = Field(description="Target repository: 'web' or 'api'")
    branch_name: str = Field(description="Branch name to merge into main")

class MergeWorktreeTool(BaseTool):
    name: str = "merge_git_branch"
    description: str = "Merges a completed worker branch into the main integration branch."
    args_schema: Type[BaseModel] = MergeWorktreeInput

    def _run(self, repo: Literal["web", "api"], branch_name: str) -> str:
        base_dir = Path(__file__).resolve().parents[4]
        repo_dir = base_dir / repo

        checkout_cmd = ["git", "-C", str(repo_dir), "checkout", "main"]
        checkout_res = subprocess.run(checkout_cmd, capture_output=True, text=True)
        if checkout_res.returncode != 0:
            return f"Failed to checkout main: {checkout_res.stderr.strip()}"

        merge_cmd = [
            "git",
            "-C",
            str(repo_dir),
            "merge",
            "--no-ff",
            "-m",
            f"merge({repo}): integrate {branch_name}",
            branch_name,
        ]
        merge_res = subprocess.run(merge_cmd, capture_output=True, text=True)
        if merge_res.returncode != 0:
            return f"Failed to merge {branch_name}: {merge_res.stderr.strip()}"

        return f"Successfully merged {branch_name} into {repo}/main"

class RemoveWorktreeInput(BaseModel):
    repo: Literal["web", "api"] = Field(description="Target repository: 'web' or 'api'")
    worktree_name: str = Field(description="Directory name of the worktree inside trees/")
    delete_branch: bool = Field(default=True, description="Whether to also delete the local git branch")
    branch_name: str | None = Field(default=None, description="Optional branch name to delete")

class RemoveWorktreeTool(BaseTool):
    name: str = "remove_git_worktree"
    description: str = "Removes a temporary Git worktree and prunes its associated branch."
    args_schema: Type[BaseModel] = RemoveWorktreeInput

    def _run(
        self,
        repo: Literal["web", "api"],
        worktree_name: str,
        delete_branch: bool = True,
        branch_name: str | None = None,
    ) -> str:
        base_dir = Path(__file__).resolve().parents[4]
        repo_dir = base_dir / repo
        worktree_path = base_dir / "trees" / worktree_name

        remove_cmd = ["git", "-C", str(repo_dir), "worktree", "remove", "--force", str(worktree_path)]
        subprocess.run(remove_cmd, capture_output=True, text=True)

        if delete_branch and branch_name:
            branch_cmd = ["git", "-C", str(repo_dir), "branch", "-D", branch_name]
            subprocess.run(branch_cmd, capture_output=True, text=True)

        return f"Worktree {worktree_name} removed successfully."
