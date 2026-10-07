import json
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any
from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel, Field

from .tools.agy_cli_tools import AgyWorkerTool
from .tools.archive_task_tools import archive_task_file
from .tools.blast_radius_tools import check_worktree_blast_radius
from .tools.git_worktree_tools import CreateWorktreeTool, MergeWorktreeTool, RemoveWorktreeTool
from .tools.self_healing_tools import attempt_quality_gate_healing
from .tools.submodule_sync_tools import sync_monorepo_submodules
from .tools.task_discovery_tools import DiscoverPendingTasksTool, DiscoveredTask, get_disjoint_waves

def get_state_dir() -> Path:
    base_dir = Path(__file__).resolve().parents[3]
    state_dir = base_dir / ".orchestrator" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir

def persist_flow_state(state: "BuscaTunidoFlowState") -> None:
    state_dir = get_state_dir()
    state_file = state_dir / f"{state.id}.json"
    latest_file = state_dir / "latest_run.json"
    payload = state.model_dump_json(indent=2)
    state_file.write_text(payload, encoding="utf-8")
    latest_file.write_text(payload, encoding="utf-8")

class BuscaTunidoFlowState(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tasks_summary: str = Field(default="")
    status: str = Field(default="PENDING")
    total_waves: int = Field(default=0)
    completed_waves: int = Field(default=0)
    executed_tasks: list[str] = Field(default_factory=list)
    quality_gate_report: str = Field(default="")
    execution_result: str = Field(default="")

class BuscaTunidoFlow(Flow[BuscaTunidoFlowState]):
    initial_state = BuscaTunidoFlowState

    @start()
    def discover_specs(self) -> str:
        discovery_tool = DiscoverPendingTasksTool()
        summary = discovery_tool.run(repo="both")
        self.state.tasks_summary = summary
        persist_flow_state(self.state)
        return summary

    @listen(discover_specs)
    def execute_waves(self, summary: str) -> str:
        if "No pending task specifications" in summary:
            self.state.status = "COMPLETED"
            self.state.execution_result = "No pending task specifications found in web/tasks or api/tasks."
            persist_flow_state(self.state)
            return self.state.execution_result

        waves = get_disjoint_waves(repo="both")
        self.state.total_waves = len(waves)
        base_dir = Path(__file__).resolve().parents[3]

        create_wt_tool = CreateWorktreeTool()
        merge_wt_tool = MergeWorktreeTool()
        remove_wt_tool = RemoveWorktreeTool()
        worker_tool = AgyWorkerTool()

        overall_logs: list[str] = []

        for wave_num in sorted(waves.keys()):
            wave_tasks = waves[wave_num]
            wave_header = f"=== RUNNING DAG WAVE {wave_num} ({len(wave_tasks)} parallel task(s)) ==="
            overall_logs.append(wave_header)

            task_worktrees: dict[str, Path] = {}
            for task in wave_tasks:
                create_wt_tool.run(repo=task.repo, branch_name=task.branch_name)
                safe_branch = task.branch_name.replace("/", "-")
                wt_path = base_dir / "trees" / f"{task.repo}.{safe_branch}"
                task_worktrees[task.task_id] = wt_path

            worker_futures = {}
            with ThreadPoolExecutor(max_workers=min(2, max(1, len(wave_tasks)))) as executor:
                for task in wave_tasks:
                    wt_path = task_worktrees[task.task_id]
                    instructions = f"Implement task specification from {task.task_file}. Commit with: {task.commit_message}"
                    future = executor.submit(
                        worker_tool._run,
                        worktree_path=str(wt_path),
                        task_instructions=instructions,
                        target_files=task.target_files,
                        commit_message=task.commit_message,
                    )
                    worker_futures[future] = task

            worker_results: dict[str, str] = {}
            for future in as_completed(worker_futures):
                task = worker_futures[future]
                worker_res = future.result()
                worker_results[task.task_id] = worker_res
                overall_logs.append(f"[{task.task_id}]: {worker_res}")

            wave_failed = False
            for task in wave_tasks:
                res_str = worker_results.get(task.task_id, "")
                if res_str.startswith("Error:") or "Worker failed" in res_str:
                    wave_failed = True
                    overall_logs.append(f"[{task.task_id} EXECUTION FAILED]: {res_str}")

            if wave_failed:
                for task in wave_tasks:
                    remove_wt_tool.run(repo=task.repo, branch_name=task.branch_name)
                self.state.status = f"FAILED_AT_WAVE_{wave_num}"
                self.state.execution_result = "\n".join(overall_logs)
                persist_flow_state(self.state)
                return self.state.execution_result

            for task in wave_tasks:
                wt_path = task_worktrees[task.task_id]
                valid, rogue, blast_msg = check_worktree_blast_radius(wt_path, task.target_files)
                if not valid:
                    overall_logs.append(f"[{task.task_id} BLAST VIOLATION]: {blast_msg}")

            for task in wave_tasks:
                merge_res = merge_wt_tool.run(repo=task.repo, branch_name=task.branch_name)
                overall_logs.append(f"[MERGE {task.task_id}]: {merge_res}")
                remove_res = remove_wt_tool.run(repo=task.repo, branch_name=task.branch_name)
                overall_logs.append(f"[CLEANUP {task.task_id}]: {remove_res}")


            repos_in_wave = {t.repo for t in wave_tasks}
            gate_target = "both" if len(repos_in_wave) > 1 else list(repos_in_wave)[0]
            passed, gate_summary = attempt_quality_gate_healing(target=gate_target, max_retries=2)
            overall_logs.append(f"[QUALITY GATE WAVE {wave_num}]:\n{gate_summary}")

            if not passed:
                self.state.status = f"FAILED_AT_WAVE_{wave_num}"
                self.state.quality_gate_report = gate_summary
                self.state.execution_result = "\n".join(overall_logs)
                persist_flow_state(self.state)
                return self.state.execution_result

            for task in wave_tasks:
                arch_ok, arch_msg = archive_task_file(task.repo, task.task_file)
                overall_logs.append(f"[ARCHIVE {task.task_id}]: {arch_msg}")
                self.state.executed_tasks.append(task.task_id)

            self.state.completed_waves += 1
            persist_flow_state(self.state)

        self.state.status = "EXECUTED"
        self.state.execution_result = "\n".join(overall_logs)
        persist_flow_state(self.state)
        return self.state.execution_result

    @listen(execute_waves)
    def finalize_orchestration(self, result: str) -> str:
        if self.state.status == "EXECUTED":
            sync_ok, sync_msg = sync_monorepo_submodules()
            self.state.status = "COMPLETED"
            self.state.execution_result += f"\n\n[SUBMODULE SYNC]: {sync_msg}"
        persist_flow_state(self.state)
        return self.state.execution_result
