import uuid
from typing import Any
from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel, Field

from .crew import BuscaTunidoCrew
from .tools.task_discovery_tools import DiscoverPendingTasksTool
from .tools.verification_tools import RunQualityGateTool

class BuscaTunidoFlowState(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tasks_summary: str = Field(default="")
    status: str = Field(default="PENDING")
    quality_gate_report: str = Field(default="")
    execution_result: str = Field(default="")

class BuscaTunidoFlow(Flow[BuscaTunidoFlowState]):
    initial_state = BuscaTunidoFlowState

    @start()
    def discover_specs(self) -> str:
        discovery_tool = DiscoverPendingTasksTool()
        summary = discovery_tool.run(repo="both")
        self.state.tasks_summary = summary
        return summary

    @listen(discover_specs)
    def run_crew_pipeline(self, summary: str) -> str:
        if "No pending task specifications" in summary:
            self.state.status = "COMPLETED"
            self.state.execution_result = "No pending task specifications found in web/tasks or api/tasks."
            return self.state.execution_result

        crew_instance = BuscaTunidoCrew()
        result = crew_instance.crew().kickoff(
            inputs={
                "tasks_summary": summary,
                "task_id": "PENDING",
                "worktree_path": "auto",
                "target_files": "auto",
                "task_instructions": summary,
                "commit_message": "feat: canonical crewai flow execution",
                "branches": "auto",
                "repo": "both",
                "worktrees": "auto",
            }
        )
        self.state.execution_result = str(result)
        self.state.status = "EXECUTED"
        return str(result)

    @listen(run_crew_pipeline)
    def verify_quality_gate(self, result: str) -> str:
        gate_tool = RunQualityGateTool()
        report = gate_tool.run(target="both")
        self.state.quality_gate_report = report
        return report
