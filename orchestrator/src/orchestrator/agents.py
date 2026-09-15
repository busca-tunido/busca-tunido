from typing import Any
from crewai import Agent
from .tools import (
    CreateWorktreeTool,
    MergeWorktreeTool,
    RemoveWorktreeTool,
    AgyWorkerTool,
    RunQualityGateTool,
)

def create_lead_orchestrator(llm: Any = None) -> Agent:
    return Agent(
        role="Lead Architecture & Wave Planner",
        goal="Decompose system requirements into parallel waves with disjoint file sets and manage git worktrees.",
        backstory=(
            "Principal Software Architect specialized in monorepo topology, spec-driven engineering, "
            "and multi-agent worktree isolation without file collisions."
        ),
        tools=[CreateWorktreeTool(), RemoveWorktreeTool()],
        verbose=True,
        llm=llm,
    )

def create_code_worker(llm: Any = None) -> Agent:
    return Agent(
        role="Pure Code Implementer",
        goal="Implement code strictly within assigned files using agy CLI without running heavy build/check tools.",
        backstory=(
            "Expert Software Engineer that produces strictly-typed, clean code. "
            "Follows the token-efficiency policy: never runs builds or lints in the worker context, "
            "focusing purely on writing correct implementation logic and committing."
        ),
        tools=[AgyWorkerTool()],
        verbose=True,
        llm=llm,
    )

def create_quality_integrator(llm: Any = None) -> Agent:
    return Agent(
        role="Centralized Quality Integrator",
        goal="Merge worker branches, reconcile shared integration points, and execute central quality verification.",
        backstory=(
            "Staff Quality & Systems Engineer acting as the final gatekeeper. "
            "Performs branch merges and runs Biome autofix, TypeScript checks, and test suites in a single pass."
        ),
        tools=[MergeWorktreeTool(), RemoveWorktreeTool(), RunQualityGateTool()],
        verbose=True,
        llm=llm,
    )
