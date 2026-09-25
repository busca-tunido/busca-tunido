from datetime import datetime
from pathlib import Path

def get_logs_dir() -> Path:
    base_dir = Path(__file__).resolve().parents[4]
    logs_dir = base_dir / ".orchestrator" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir

def save_worker_log(
    task_id: str,
    worktree_path: str,
    prompt: str,
    stdout: str,
    stderr: str,
    returncode: int,
) -> Path:
    logs_dir = get_logs_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_task_id = task_id.replace("/", "_").replace("\\", "_")
    log_file = logs_dir / f"{timestamp}_{clean_task_id}.log"

    content = [
        f"=== WORKER RUN: {task_id} ===",
        f"Timestamp: {datetime.now().isoformat()}",
        f"Worktree: {worktree_path}",
        f"Exit Code: {returncode}",
        "",
        "--- PROMPT ---",
        prompt,
        "",
        "--- STDOUT ---",
        stdout,
        "",
        "--- STDERR ---",
        stderr,
        "",
        "=== END OF LOG ===",
    ]

    log_file.write_text("\n".join(content), encoding="utf-8")
    return log_file
