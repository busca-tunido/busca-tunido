from pathlib import Path
from typing import Any
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from .llm.agy_llm import AgyLLM
from .tools import (
    AgyWorkerTool,
    CreateWorktreeTool,
    DiscoverPendingTasksTool,
    ListWorktreesTool,
    MergeWorktreeTool,
    RemoveWorktreeTool,
    RunQualityGateTool,
)

@CrewBase
class BuscaTunidoCrew:
    agents_config = "../../config/agents.yaml"
    tasks_config = "../../config/tasks.yaml"

    def __init__(self, llm: Any = None) -> None:
        self.llm = llm or AgyLLM()
        self.skills_dir = str(Path(__file__).resolve().parents[2] / "skills")

    @agent
    def lead_orchestrator(self) -> Agent:
        return Agent(
            config=self.agents_config["lead_orchestrator"],
            tools=[
                DiscoverPendingTasksTool(),
                CreateWorktreeTool(),
                ListWorktreesTool(),
                RemoveWorktreeTool(),
            ],
            skills=[f"{self.skills_dir}/worktree-orchestration"],
            llm=self.llm,
            verbose=True,
        )

    @agent
    def code_worker(self) -> Agent:
        return Agent(
            config=self.agents_config["code_worker"],
            tools=[AgyWorkerTool()],
            skills=[f"{self.skills_dir}/token-efficient-coding"],
            llm=self.llm,
            verbose=True,
        )

    @agent
    def quality_integrator(self) -> Agent:
        return Agent(
            config=self.agents_config["quality_integrator"],
            tools=[
                MergeWorktreeTool(),
                RemoveWorktreeTool(),
                ListWorktreesTool(),
                RunQualityGateTool(),
            ],
            skills=[f"{self.skills_dir}/centralized-quality-gate"],
            llm=self.llm,
            verbose=True,
        )

    @task
    def plan_waves_task(self) -> Task:
        return Task(
            config=self.tasks_config["plan_waves_task"],
        )

    @task
    def execute_worker_task(self) -> Task:
        return Task(
            config=self.tasks_config["execute_worker_task"],
        )

    @task
    def integrate_quality_gate_task(self) -> Task:
        return Task(
            config=self.tasks_config["integrate_quality_gate_task"],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.lead_orchestrator(), self.code_worker(), self.quality_integrator()],
            tasks=[self.plan_waves_task(), self.execute_worker_task(), self.integrate_quality_gate_task()],
            process=Process.sequential,
            verbose=True,
        )
