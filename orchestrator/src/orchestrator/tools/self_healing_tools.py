import shutil
import subprocess
from pathlib import Path
from typing import Literal, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from orchestrator.tools.verification_tools import RunQualityGateTool
from orchestrator.utils.logger import save_worker_log

def run_healing_agent(target_dir: Path, error_report: str) -> tuple[int, str, str]:
    healing_prompt = (
        "You are an expert Systems Integration and Quality Gate Fixer.\n"
        "The centralized quality gate check failed with the following errors:\n\n"
        f"{error_report}\n\n"
        "STRICT INSTRUCTIONS:\n"
        "1. Fix the compile/typecheck, Biome lint, or test failures directly in the necessary files.\n"
        "2. Adhere to strict typing standards. Do not use 'any'.\n"
        "3. Do not write comments inside code.\n"
        "4. Do not alter package.json or dependencies.\n"
        "5. Once resolved, stage only the repaired files with 'git add' and commit with: 'fix(quality-gate): resolve static analysis and test diagnostics'. Then exit."
    )

    agy_bin = shutil.which("agy.exe") or shutil.which("agy") or "agy.exe"
    cmd = [
        agy_bin,
        "--model",
        "gemini-3.8-flash-high",
        "--add-dir",
        str(target_dir),
        "-p",
        healing_prompt,
        "--mode",
        "accept-edits",
        "--dangerously-skip-permissions",
    ]

    res = subprocess.run(
        cmd,
        cwd=str(target_dir),
        capture_output=True,
        text=True,
        timeout=600,
    )

    save_worker_log(
        task_id=f"HEAL_{target_dir.name}",
        worktree_path=str(target_dir),
        prompt=healing_prompt,
        stdout=res.stdout,
        stderr=res.stderr,
        returncode=res.returncode,
    )

    return res.returncode, res.stdout, res.stderr

def attempt_quality_gate_healing(
    target: Literal["web", "api", "both"],
    max_retries: int = 2,
) -> tuple[bool, str]:
    gate_tool = RunQualityGateTool()
    base_dir = Path(__file__).resolve().parents[4]

    report = gate_tool.run(target=target)
    if "FAILED" not in report:
        return True, f"Initial Quality Gate passed cleanly.\n{report}"

    retries = 0
    history: list[str] = [f"Initial gate failed:\n{report}"]

    while retries < max_retries and "FAILED" in report:
        retries += 1
        targets_to_heal = []
        if target in ("web", "both") and "[WEB GATE - FAILED]" in report:
            targets_to_heal.append("web")
        if target in ("api", "both") and "[API GATE - FAILED]" in report:
            targets_to_heal.append("api")

        for t in targets_to_heal:
            repo_dir = base_dir / t
            code, stdout, stderr = run_healing_agent(repo_dir, report)
            history.append(f"[Retry {retries} for {t}] Healing agent exit code: {code}")

        report = gate_tool.run(target=target)
        if "FAILED" not in report:
            history.append(f"Quality gate PASSED on healing retry {retries}!")
            return True, "\n\n".join(history)

    return False, f"Quality gate failed after {max_retries} healing retries.\n" + "\n\n".join(history)

class SelfHealingInput(BaseModel):
    target: Literal["web", "api", "both"] = Field(
        default="both",
        description="Target submodule to verify and self-heal: 'web', 'api', or 'both'",
    )
    max_retries: int = Field(default=2, description="Maximum number of self-healing repair attempts")

class SelfHealingQualityGateTool(BaseTool):
    name: str = "self_healing_quality_gate"
    description: str = "Executes the centralized quality gate and automatically launches healing workers to fix static or test failures."
    args_schema: Type[BaseModel] = SelfHealingInput

    def _run(self, target: Literal["web", "api", "both"] = "both", max_retries: int = 2) -> str:
        passed, summary = attempt_quality_gate_healing(target, max_retries=max_retries)
        return summary
