import subprocess
from pathlib import Path
from typing import Literal, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class RunQualityGateInput(BaseModel):
    target: Literal["web", "api", "both"] = Field(description="Target submodule to verify: 'web', 'api', or 'both'")

class RunQualityGateTool(BaseTool):
    name: str = "run_quality_gate"
    description: str = "Runs centralized Biome linting, typecheck, and test suite on the integrated branch."
    args_schema: Type[BaseModel] = RunQualityGateInput

    def _run_submodule_gate(self, repo_dir: Path, is_web: bool) -> tuple[bool, str]:
        logs: list[str] = []

        check_res = subprocess.run(["pnpm", "run", "check"], cwd=str(repo_dir), capture_output=True, text=True, shell=True)
        if check_res.returncode != 0:
            logs.append(f"Biome autofix error:\n{check_res.stderr.strip() or check_res.stdout.strip()}")

        typecheck_cmd = ["pnpm", "exec", "tsc", "--noEmit"] if is_web else ["pnpm", "run", "build"]
        tsc_res = subprocess.run(typecheck_cmd, cwd=str(repo_dir), capture_output=True, text=True, shell=True)
        if tsc_res.returncode != 0:
            logs.append(f"Typecheck / Build error:\n{tsc_res.stderr.strip() or tsc_res.stdout.strip()}")

        review_res = subprocess.run(["pnpm", "run", "review"], cwd=str(repo_dir), capture_output=True, text=True, shell=True)
        if review_res.returncode != 0:
            logs.append(f"Biome review error:\n{review_res.stderr.strip() or review_res.stdout.strip()}")

        test_res = subprocess.run(["pnpm", "vitest", "run"], cwd=str(repo_dir), capture_output=True, text=True, shell=True)
        if test_res.returncode != 0:
            logs.append(f"Unit test failures:\n{test_res.stderr.strip() or test_res.stdout.strip()[-500:]}")

        passed = len(logs) == 0
        summary = "All checks passed cleanly." if passed else "\n\n".join(logs)
        return passed, summary

    def _run(self, target: Literal["web", "api", "both"]) -> str:
        base_dir = Path(__file__).resolve().parents[4]
        results: list[str] = []

        targets = ["web", "api"] if target == "both" else [target]

        for t in targets:
            repo_path = base_dir / t
            is_web = t == "web"
            passed, report = self._run_submodule_gate(repo_path, is_web=is_web)
            status = "PASSED" if passed else "FAILED"
            results.append(f"[{t.upper()} GATE - {status}]\n{report}")

        return "\n\n".join(results)
