import shutil
import subprocess
from pathlib import Path
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class AgyWorkerInput(BaseModel):
    worktree_path: str = Field(description="Absolute or relative path to the worker's git worktree")
    task_instructions: str = Field(description="Specific technical instructions for the code to implement")
    target_files: list[str] = Field(description="List of exclusive target files that the worker is permitted to edit")
    commit_message: str = Field(description="Single-line conventional commit message for the change")

class AgyWorkerTool(BaseTool):
    name: str = "run_agy_worker"
    description: str = "Dispatches a lean agy worker agent to implement code in an isolated worktree."
    args_schema: Type[BaseModel] = AgyWorkerInput

    def _run(
        self,
        worktree_path: str,
        task_instructions: str,
        target_files: list[str],
        commit_message: str,
    ) -> str:
        resolved_path = Path(worktree_path).resolve()
        if not resolved_path.exists():
            return f"Error: Worktree path does not exist: {resolved_path}"

        files_list = ", ".join(target_files)
        lean_prompt = (
            f"You are a pure Code Implementer worker.\n"
            f"Target Files (Exclusive): {files_list}\n"
            f"Task: {task_instructions}\n\n"
            f"STRICT RULES:\n"
            f"1. Implement the requested logic strictly within your Target Files.\n"
            f"2. Use standard strict typing notations. Do not use 'any'.\n"
            f"3. Do not write comments inside code.\n"
            f"4. DO NOT run pnpm build, tsc, nest build, or biome check. Quality verification is handled centrally by the Integrator.\n"
            f"5. Once finished, stage only your target files using 'git add' and commit with: '{commit_message}'. Then exit."
        )

        agy_bin = shutil.which("agy.exe") or shutil.which("agy") or "agy.exe"
        cmd = [
            agy_bin,
            "--model",
            "gemini-3.7-flash-high",
            "--add-dir",
            str(resolved_path),
            "-p",
            lean_prompt,
            "--mode",
            "accept-edits",
            "--dangerously-skip-permissions",
        ]

        try:
            res = subprocess.run(
                cmd,
                cwd=str(resolved_path),
                capture_output=True,
                text=True,
                timeout=600,
            )
            if res.returncode != 0:
                return f"Worker completed with error: {res.stderr.strip()}\nOutput: {res.stdout.strip()[:500]}"
            return f"Worker completed successfully.\nOutput: {res.stdout.strip()[-300:]}"
        except subprocess.TimeoutExpired:
            return "Error: Worker process timed out after 10 minutes."
        except FileNotFoundError:
            return "Error: agy.exe not found in PATH."
