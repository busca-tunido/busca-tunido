from typing import Any
from crewai import Crew, Process
from .agents import create_lead_orchestrator, create_code_worker, create_quality_integrator
from .tasks import create_planning_task, create_integration_task

class BuscaTunidoCrew:
    def __init__(self, llm: Any = None) -> None:
        self.llm = llm
        self.orchestrator = create_lead_orchestrator(llm)
        self.worker = create_code_worker(llm)
        self.integrator = create_quality_integrator(llm)

    def run_planning(self, requirement: str) -> str:
        try:
            task = create_planning_task(self.orchestrator, requirement)
            crew = Crew(
                agents=[self.orchestrator],
                tasks=[task],
                process=Process.sequential,
                verbose=True,
            )
            return str(crew.kickoff())
        except Exception as exc:
            return (
                f"Error during CrewAI planning: {exc}\n"
                "Tip: CrewAI autonomous planning requires OPENAI_API_KEY. "
                "For pre-planned DAG waves, use the deterministic 'run-wave <N>' command instead."
            )

    def run_integration(self, repo: str, branches: list[str], worktrees: list[str]) -> str:
        try:
            task = create_integration_task(self.integrator, repo, branches, worktrees)
            crew = Crew(
                agents=[self.integrator],
                tasks=[task],
                process=Process.sequential,
                verbose=True,
            )
            return str(crew.kickoff())
        except Exception as exc:
            return f"Error during CrewAI integration: {exc}"
