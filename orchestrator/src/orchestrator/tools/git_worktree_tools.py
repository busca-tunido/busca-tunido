import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Literal, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

def get_wt_bin() -> str:
    return shutil.which("wt.exe") or shutil.which("wt") or "wt"

def get_wt_config_path(base_dir: Path) -> Path:
    return base_dir / "orchestrator" / "config" / "wt.toml"

def get_trees_dir(base_dir: Path) -> Path:
    trees_dir = base_dir / "trees"
    trees_dir.mkdir(parents=True, exist_ok=True)
    return trees_dir

def get_worktree_path(base_dir: Path, repo: str, branch_name: str) -> Path:
    safe_branch = branch_name.replace("/", "-")
    return get_trees_dir(base_dir) / f"{repo}.{safe_branch}"

class CreateWorktreeInput(BaseModel):
    repo: Literal["web", "api"] = Field(description="Target repository: 'web' or 'api'")
    branch_name: str = Field(description="New git branch name for the worker")

class CreateWorktreeTool(BaseTool):
    name: str = "create_worktrunk_worktree"
    description: str = "Creates an isolated Git worktree and branch inside trees/ using worktrunk (wt) for a parallel worker agent."
    args_schema: Type[BaseModel] = CreateWorktreeInput

    def _run(self, repo: Literal["web", "api"], branch_name: str) -> str:
        base_dir = Path(__file__).resolve().parents[4]
        repo_dir = base_dir / repo
        get_trees_dir(base_dir)
        cfg_file = get_wt_config_path(base_dir)

        wt_bin = get_wt_bin()
        cmd_env = os.environ.copy()
        if cfg_file.exists():
            cmd_env["WORKTRUNK_CONFIG_PATH"] = str(cfg_file)

        remove_cmd = [wt_bin, "-C", str(repo_dir)]
        if cfg_file.exists():
            remove_cmd.extend(["--config", str(cfg_file)])
        remove_cmd.extend(["remove", "--force", branch_name, "-D"])
        subprocess.run(remove_cmd, env=cmd_env, capture_output=True, text=True)

        switch_cmd = [wt_bin, "-C", str(repo_dir)]
        if cfg_file.exists():
            switch_cmd.extend(["--config", str(cfg_file)])
        switch_cmd.extend(["switch", "--create", branch_name])
        res = subprocess.run(switch_cmd, env=cmd_env, capture_output=True, text=True)
        if res.returncode != 0:
            return f"Failed to create worktree with wt: {res.stderr.strip() or res.stdout.strip()}"

        list_cmd = [wt_bin, "-C", str(repo_dir)]
        if cfg_file.exists():
            list_cmd.extend(["--config", str(cfg_file)])
        list_cmd.extend(["list", "--format", "json"])
        list_res = subprocess.run(list_cmd, env=cmd_env, capture_output=True, text=True)
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
            worktree_path = str(get_worktree_path(base_dir, repo, branch_name))

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
    description: str = "Removes a worktree from trees/ and deletes its branch using worktrunk (wt)."
    args_schema: Type[BaseModel] = RemoveWorktreeInput

    def _run(self, repo: Literal["web", "api"], branch_name: str) -> str:
        base_dir = Path(__file__).resolve().parents[4]
        repo_dir = base_dir / repo
        cfg_file = get_wt_config_path(base_dir)

        wt_bin = get_wt_bin()
        cmd_env = os.environ.copy()
        if cfg_file.exists():
            cmd_env["WORKTRUNK_CONFIG_PATH"] = str(cfg_file)

        cmd = [wt_bin, "-C", str(repo_dir)]
        if cfg_file.exists():
            cmd.extend(["--config", str(cfg_file)])
        cmd.extend(["remove", "--force", branch_name, "-D"])
        res = subprocess.run(cmd, env=cmd_env, capture_output=True, text=True)
        if res.returncode != 0:
            return f"Failed to remove worktree {branch_name} with wt: {res.stderr.strip() or res.stdout.strip()}"

        return f"Successfully removed worktree and branch '{branch_name}' via worktrunk."

class ListWorktreesInput(BaseModel):
    repo: Literal["web", "api"] = Field(description="Target repository: 'web' or 'api'")

class ListWorktreesTool(BaseTool):
    name: str = "list_worktrunk_worktrees"
    description: str = "Lists active worktrees in trees/ and their status using worktrunk (wt)."
    args_schema: Type[BaseModel] = ListWorktreesInput

    def _run(self, repo: Literal["web", "api"]) -> str:
        base_dir = Path(__file__).resolve().parents[4]
        repo_dir = base_dir / repo
        cfg_file = get_wt_config_path(base_dir)

        wt_bin = get_wt_bin()
        cmd_env = os.environ.copy()
        if cfg_file.exists():
            cmd_env["WORKTRUNK_CONFIG_PATH"] = str(cfg_file)

        cmd = [wt_bin, "-C", str(repo_dir)]
        if cfg_file.exists():
            cmd.extend(["--config", str(cfg_file)])
        cmd.append("list")
        res = subprocess.run(cmd, env=cmd_env, capture_output=True, text=True)
        if res.returncode != 0:
            return f"Failed to list worktrees with wt: {res.stderr.strip()}"

        return res.stdout.strip()
