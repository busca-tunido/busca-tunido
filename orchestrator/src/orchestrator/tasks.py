from crewai import Agent, Task

def create_planning_task(agent: Agent, requirement: str) -> Task:
    return Task(
        description=(
            f"Analyze requirement: '{requirement}'.\n"
            f"1. Break it down into sub-tasks with strict disjoint file sets.\n"
            f"2. Determine whether tasks belong to 'web', 'api', or both.\n"
            f"3. Create necessary isolated git worktrees using 'create_git_worktree' for each parallel task.\n"
            f"Return a structured execution plan with task IDs, target files, and worktree paths."
        ),
        expected_output="Structured execution plan with worktree paths and assigned exclusive target files.",
        agent=agent,
    )

def create_worker_task(
    agent: Agent,
    worktree_path: str,
    task_instructions: str,
    target_files: list[str],
    commit_message: str,
) -> Task:
    files_str = ", ".join(target_files)
    return Task(
        description=(
            f"Execute code implementation in worktree '{worktree_path}'.\n"
            f"Target Files: {files_str}\n"
            f"Instructions: {task_instructions}\n"
            f"Use 'run_agy_worker' to implement the code. Do not run build or lint tools.\n"
            f"Commit message: '{commit_message}'."
        ),
        expected_output="Confirmation of code changes committed in the worktree.",
        agent=agent,
    )

def create_integration_task(
    agent: Agent,
    repo: str,
    branches: list[str],
    worktrees: list[str],
) -> Task:
    branches_str = ", ".join(branches)
    worktrees_str = ", ".join(worktrees)
    return Task(
        description=(
            f"Integrate completed branches: {branches_str} into '{repo}/main'.\n"
            f"1. Use 'merge_git_branch' for each branch.\n"
            f"2. Run 'run_quality_gate' for target '{repo}'.\n"
            f"3. If checks pass, remove temporary worktrees: {worktrees_str} using 'remove_git_worktree'.\n"
            f"4. If errors occur, summarize the exact compiler errors for the queue."
        ),
        expected_output="Quality gate report and branch integration status.",
        agent=agent,
    )
