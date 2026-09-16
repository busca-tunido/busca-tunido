import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .tools.agy_cli_tools import AgyWorkerTool
from .tools.git_worktree_tools import CreateWorktreeTool, MergeWorktreeTool, RemoveWorktreeTool
from .tools.verification_tools import RunQualityGateTool

@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    repo: Literal["web", "api"]
    branch_name: str
    task_file: str
    target_files: list[str]
    commit_message: str

@dataclass(frozen=True)
class WaveSpec:
    wave_number: int
    description: str
    tasks: list[TaskSpec]

WAVES: dict[int, WaveSpec] = {
    1: WaveSpec(
        wave_number=1,
        description="Infraestructura de Caché, Paginación Backend y Cliente en Paralelo",
        tasks=[
            TaskSpec(
                task_id="API-021",
                repo="api",
                branch_name="feat/021-http-caching-headers",
                task_file="tasks/021_http-caching-headers.md",
                target_files=[
                    "src/common/interceptors/cache-control.interceptor.ts",
                    "src/universities/universities.controller.ts",
                ],
                commit_message="perf(api): add http cache-control headers for static endpoints",
            ),
            TaskSpec(
                task_id="API-022",
                repo="api",
                branch_name="feat/022-reviews-pagination",
                task_file="tasks/022_reviews-pagination-backend.md",
                target_files=[
                    "src/reviews/dto/filter-reviews.dto.ts",
                    "src/reviews/reviews.service.ts",
                    "src/reviews/reviews.controller.ts",
                ],
                commit_message="feat(reviews): add server-side pagination and filters to pension reviews",
            ),
            TaskSpec(
                task_id="WEB-038",
                repo="web",
                branch_name="feat/038-swr-cache-foundation",
                task_file="tasks/038_shared-swr-cache-foundation.md",
                target_files=[
                    "src/lib/cache-store.ts",
                    "src/hooks/use-cached-query.ts",
                ],
                commit_message="feat(cache): implement shared in-memory swr cache store",
            ),
            TaskSpec(
                task_id="WEB-039",
                repo="web",
                branch_name="feat/039-reviews-pagination-sync",
                task_file="tasks/039_reviews-pagination-client-sync.md",
                target_files=[
                    "src/services/reviews.service.ts",
                    "src/lib/api-client.ts",
                ],
                commit_message="feat(reviews): sync client data layer with server-side pagination",
            ),
        ],
    ),
    2: WaveSpec(
        wave_number=2,
        description="Hooks Reactivos con Caché y Formularios con Reducers en Paralelo",
        tasks=[
            TaskSpec(
                task_id="WEB-040",
                repo="web",
                branch_name="feat/040-adopt-cache-in-hooks",
                task_file="tasks/040_adopt-cache-in-hooks.md",
                target_files=[
                    "src/hooks/use-pension-detail.ts",
                    "src/hooks/use-pension-reviews.ts",
                    "src/hooks/use-universities.ts",
                ],
                commit_message="feat(hooks): integrate shared swr cache and pagination in data hooks",
            ),
            TaskSpec(
                task_id="WEB-041",
                repo="web",
                branch_name="feat/041-modal-reducers",
                task_file="tasks/041_modal-reducers-state-machines.md",
                target_files=[
                    "src/reducers/suggest-edit-reducer.ts",
                    "src/reducers/publish-review-reducer.ts",
                    "src/components/pensions/suggest-edit-modal.tsx",
                    "src/components/reviews/publish-review-modal.tsx",
                ],
                commit_message="refactor(modals): convert complex forms to useReducer state machines",
            ),
        ],
    ),
    3: WaveSpec(
        wave_number=3,
        description="Renderizado en Servidor y Context Slicing en Paralelo",
        tasks=[
            TaskSpec(
                task_id="WEB-042",
                repo="web",
                branch_name="feat/042-context-slicing",
                task_file="tasks/042_context-slicing-navigation-and-filters.md",
                target_files=[
                    "src/contexts/navigation-context.tsx",
                    "src/contexts/search-filters-context.tsx",
                    "src/components/shells/student-app-shell.tsx",
                ],
                commit_message="refactor(shell): slice state into navigation and filters contexts",
            ),
            TaskSpec(
                task_id="WEB-043",
                repo="web",
                branch_name="feat/043-rsc-prefetch-seo",
                task_file="tasks/043_rsc-initial-prefetch-and-seo.md",
                target_files=[
                    "src/app/page.tsx",
                    "src/components/shells/role-router.tsx",
                ],
                commit_message="perf(ssr): implement server component prefetch for initial feed",
            ),
        ],
    ),
    4: WaveSpec(
        wave_number=4,
        description="Rendimiento de Renderizado y Mapa en Paralelo",
        tasks=[
            TaskSpec(
                task_id="WEB-044",
                repo="web",
                branch_name="feat/044-pension-card-memo",
                task_file="tasks/044_pension-card-memo-and-virtual-list.md",
                target_files=[
                    "src/components/pensions/pension-card.tsx",
                    "src/components/pensions/infinite-pension-list.tsx",
                ],
                commit_message="perf(pensions): memoize PensionCard and optimize infinite list rendering",
            ),
            TaskSpec(
                task_id="WEB-045",
                repo="web",
                branch_name="feat/045-map-clustering",
                task_file="tasks/045_map-marker-clustering-and-canvas.md",
                target_files=[
                    "src/components/map/map-screen.tsx",
                ],
                commit_message="perf(map): implement zoom-aware marker rendering and clustering",
            ),
        ],
    ),
    5: WaveSpec(
        wave_number=5,
        description="Compuerta Centralizada Avanzada de Calidad Frontend y Backend",
        tasks=[
            TaskSpec(
                task_id="WEB-046",
                repo="web",
                branch_name="chore/046-advanced-quality-gate",
                task_file="tasks/046_advanced-frontend-quality-gate.md",
                target_files=[],
                commit_message="chore(quality): advanced frontend and backend quality gate verification",
            ),
        ],
    ),
}

import concurrent.futures

class WaveRunner:
    def __init__(self) -> None:
        self.base_dir = Path(__file__).resolve().parents[3]
        self.create_tool = CreateWorktreeTool()
        self.merge_tool = MergeWorktreeTool()
        self.remove_tool = RemoveWorktreeTool()
        self.worker_tool = AgyWorkerTool()
        self.gate_tool = RunQualityGateTool()

    def resolve_worktree_path(self, repo: str, branch_name: str) -> Path:
        repo_dir = self.base_dir / repo
        list_cmd = ["wt", "-C", str(repo_dir), "list", "--format", "json"]
        list_res = subprocess.run(list_cmd, capture_output=True, text=True)
        if list_res.returncode == 0:
            try:
                data = json.loads(list_res.stdout)
                for item in data.get("items", []):
                    if item.get("branch") == branch_name:
                        found_path = item.get("worktree", {}).get("path")
                        if found_path:
                            return Path(found_path).resolve()
            except json.JSONDecodeError:
                pass
        return (self.base_dir / f"{repo}.{branch_name}").resolve()

    def run_wave(self, wave_number: int, dry_run: bool = False) -> str:
        if wave_number not in WAVES:
            return f"Error: Onda {wave_number} no definida. Ondas disponibles: {list(WAVES.keys())}"

        wave = WAVES[wave_number]
        header = f"=== EJECUTANDO ONDA {wave.wave_number}: {wave.description} ==="
        logs: list[str] = [header]

        if dry_run:
            logs.append("[DRY RUN MODE]")
            for task in wave.tasks:
                logs.append(f"  - Tarea: {task.task_id} ({task.repo})")
                logs.append(f"    Rama: {task.branch_name}")
                logs.append(f"    Archivos: {', '.join(task.target_files)}")
                logs.append(f"    Commit: {task.commit_message}")
            return "\n".join(logs)

        active_worktrees: list[tuple[TaskSpec, Path]] = []

        for task in wave.tasks:
            if not task.target_files:
                continue
            logs.append(f"\n[1/3] Provisionando worktree para {task.task_id} ({task.branch_name})...")
            create_msg = self.create_tool.run(repo=task.repo, branch_name=task.branch_name)
            logs.append(create_msg)

            wt_path = self.resolve_worktree_path(task.repo, task.branch_name)
            active_worktrees.append((task, wt_path))

        if active_worktrees:
            logs.append(f"\n[2/3] Despachando {len(active_worktrees)} Agy Workers en paralelo...")

            def _execute_worker(task_spec: TaskSpec, target_path: Path) -> tuple[TaskSpec, str]:
                task_file_path = self.base_dir / task_spec.repo / task_spec.task_file
                if task_file_path.exists():
                    task_instructions = task_file_path.read_text(encoding="utf-8")
                else:
                    task_instructions = f"Implement changes for {task_spec.task_id}. Target files: {task_spec.target_files}"

                res = self.worker_tool.run(
                    worktree_path=str(target_path),
                    task_instructions=task_instructions,
                    target_files=task_spec.target_files,
                    commit_message=task_spec.commit_message,
                )
                return task_spec, res

            with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, len(active_worktrees))) as executor:
                future_to_task = {
                    executor.submit(_execute_worker, t, p): t for t, p in active_worktrees
                }
                for future in concurrent.futures.as_completed(future_to_task):
                    task_spec, worker_output = future.result()
                    logs.append(f"\n--- Worker completado para {task_spec.task_id} ({task_spec.branch_name}) ---\n{worker_output}")

            logs.append("\n[3/3] Integrando ramas y limpiando worktrees...")
            for task, wt_path in active_worktrees:
                st_res = subprocess.run(
                    ["git", "-C", str(wt_path), "status", "--porcelain"],
                    capture_output=True,
                    text=True,
                )
                if st_res.returncode == 0 and st_res.stdout.strip():
                    subprocess.run(["git", "-C", str(wt_path), "add", "-A"])
                    subprocess.run(["git", "-C", str(wt_path), "commit", "-m", task.commit_message])

                merge_msg = self.merge_tool.run(repo=task.repo, branch_name=task.branch_name)
                logs.append(merge_msg)

                remove_msg = self.remove_tool.run(repo=task.repo, branch_name=task.branch_name)
                logs.append(remove_msg)

        logs.append("\n=== EJECUTANDO COMPUERTA CENTRALIZADA DE CALIDAD ===")
        gate_report = self.gate_tool.run(target="both")
        logs.append(gate_report)

        if "FAILED" not in gate_report:
            logs.append("\n[Archivando especificaciones de tareas completadas]")
            affected_repos: set[str] = set()
            for task in wave.tasks:
                src_task = self.base_dir / task.repo / task.task_file
                dest_task = self.base_dir / task.repo / "tasks" / "completed" / src_task.name
                if src_task.exists():
                    dest_task.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(src_task), str(dest_task))
                    logs.append(f"  - Archivada {task.task_id} -> {dest_task.name}")
                    affected_repos.add(task.repo)

            for repo in affected_repos:
                repo_path = self.base_dir / repo
                subprocess.run(["git", "-C", str(repo_path), "add", "tasks/"])
                subprocess.run(
                    ["git", "-C", str(repo_path), "commit", "-m", f"chore(tasks): archive completed wave {wave.wave_number} tasks"],
                    capture_output=True,
                )

        return "\n".join(logs)
