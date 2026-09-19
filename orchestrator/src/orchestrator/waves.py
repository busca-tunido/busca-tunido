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
        description="Filtros y Permisos Backend con Cimientos SEO y Slider en Paralelo",
        tasks=[
            TaskSpec(
                task_id="API-026",
                repo="api",
                branch_name="feat/026-pension-filters-histogram",
                task_file="tasks/pension-filters-histogram-backend.md",
                target_files=[
                    "src/pensions/dto/filter-pensions.dto.ts",
                    "src/pensions/pensions.service.ts",
                    "src/pensions/pensions.controller.ts",
                ],
                commit_message="feat(pensions): add advanced room filters and dynamic price histogram endpoint",
            ),
            TaskSpec(
                task_id="API-027",
                repo="api",
                branch_name="feat/027-landlord-proposals-permissions",
                task_file="tasks/landlord-proposals-permissions.md",
                target_files=[
                    "src/proposals/proposals.controller.ts",
                    "src/proposals/proposals.service.ts",
                ],
                commit_message="feat(proposals): authorize pension owners to review community edit proposals",
            ),
            TaskSpec(
                task_id="WEB-053",
                repo="web",
                branch_name="feat/053-seo-foundations-and-discovery",
                task_file="tasks/seo-foundations-and-discovery.md",
                target_files=[
                    "public/llms.txt",
                    "public/llms-full.txt",
                    "src/app/robots.ts",
                    "src/app/not-found.tsx",
                    "src/app/opengraph-image.tsx",
                    "src/app/layout.tsx",
                    "src/app/terms/page.tsx",
                    "src/app/privacy/page.tsx",
                    "src/app/faq/page.tsx",
                    "src/app/contact/page.tsx",
                ],
                commit_message="feat(seo): configure llms.txt, dynamic opengraph, not-found page and canonical metadata",
            ),
            TaskSpec(
                task_id="WEB-058",
                repo="web",
                branch_name="feat/058-price-histogram-slider",
                task_file="tasks/price-histogram-slider-component.md",
                target_files=[
                    "src/components/search/price-histogram-range-slider.tsx",
                ],
                commit_message="feat(search): implement airbnb-style price histogram range slider component",
            ),
        ],
    ),
    2: WaveSpec(
        wave_number=2,
        description="Listado Propietario Backend, Desbloqueo SSR, Búsqueda y Navegación Mobile en Paralelo",
        tasks=[
            TaskSpec(
                task_id="API-028",
                repo="api",
                branch_name="feat/028-landlord-pensions-mine",
                task_file="tasks/landlord-pensions-mine.md",
                target_files=[
                    "src/pensions/pensions.controller.ts",
                    "src/pensions/pensions.service.ts",
                ],
                commit_message="feat(pensions): add GET /pensions/mine endpoint for landlord property management",
            ),
            TaskSpec(
                task_id="WEB-055",
                repo="web",
                branch_name="feat/055-public-ssr-catalog",
                task_file="tasks/seo-public-ssr-catalog-viewsource.md",
                target_files=[
                    "src/components/shells/role-router.tsx",
                    "src/lib/auth-context.tsx",
                    "src/app/page.tsx",
                ],
                commit_message="feat(seo): enable public ssr catalog browsing and unblock view-source html",
            ),
            TaskSpec(
                task_id="WEB-060",
                repo="web",
                branch_name="feat/060-search-nav-viewport-sync",
                task_file="tasks/search-navigation-and-viewport-sync.md",
                target_files=[
                    "src/components/layout/desktop-navbar.tsx",
                    "src/hooks/use-map-viewport-pensions.ts",
                ],
                commit_message="fix(search): route global navbar searches to explore and sync map viewport filters",
            ),
            TaskSpec(
                task_id="WEB-049",
                repo="web",
                branch_name="feat/049-landlord-navigation-components",
                task_file="tasks/landlord-navigation-components.md",
                target_files=[
                    "src/components/layout/landlord-bottom-nav.tsx",
                    "src/components/layout/landlord-mobile-header.tsx",
                ],
                commit_message="feat(landlord): implement mobile header without logo and bottom navigation bar",
            ),
        ],
    ),
    3: WaveSpec(
        wave_number=3,
        description="Contratos de Datos, Componentes de Habitación, Propuestas y Semántica en Paralelo",
        tasks=[
            TaskSpec(
                task_id="WEB-059",
                repo="web",
                branch_name="feat/059-price-histogram-service-hook",
                task_file="tasks/price-histogram-service-hook.md",
                target_files=[
                    "src/lib/types.ts",
                    "src/services/pensions.service.ts",
                    "src/hooks/use-price-histogram.ts",
                ],
                commit_message="feat(pensions): add price histogram and landlord client services with reactive hook",
            ),
            TaskSpec(
                task_id="WEB-050",
                repo="web",
                branch_name="feat/050-landlord-room-atom-components",
                task_file="tasks/landlord-room-atom-components.md",
                target_files=[
                    "src/components/landlord/room-item-card.tsx",
                    "src/components/landlord/room-editor-drawer.tsx",
                ],
                commit_message="feat(landlord): implement room item card and mobile room editor drawer",
            ),
            TaskSpec(
                task_id="WEB-051",
                repo="web",
                branch_name="feat/051-landlord-proposals-drawer",
                task_file="tasks/landlord-proposals-drawer.md",
                target_files=[
                    "src/components/landlord/landlord-proposals-drawer.tsx",
                ],
                commit_message="feat(landlord): implement LandlordProposalsDrawer for community suggestions review",
            ),
            TaskSpec(
                task_id="WEB-056",
                repo="web",
                branch_name="feat/056-seo-semantics-structured-data",
                task_file="tasks/seo-semantics-and-structured-data.md",
                target_files=[
                    "src/components/pensions/pension-card.tsx",
                    "src/components/explore/explore-screen.tsx",
                    "src/components/shells/student-app-shell.tsx",
                    "src/components/seo/json-ld.tsx",
                ],
                commit_message="refactor(seo): enforce semantic html, heading hierarchy, dynamic titles and json-ld schemas",
            ),
        ],
    ),
    4: WaveSpec(
        wave_number=4,
        description="Filtro Airbnb, Estado Global Propietario y Pantallas Móviles en Paralelo",
        tasks=[
            TaskSpec(
                task_id="WEB-061",
                repo="web",
                branch_name="feat/061-airbnb-filter-drawer",
                task_file="tasks/airbnb-filter-drawer-redesign.md",
                target_files=[
                    "src/components/layout/filter-drawer.tsx",
                ],
                commit_message="feat(filters): redesign filter drawer with airbnb-style scrollable layout and dynamic histogram",
            ),
            TaskSpec(
                task_id="WEB-052",
                repo="web",
                branch_name="feat/052-landlord-context-state",
                task_file="tasks/landlord-context-state.md",
                target_files=[
                    "src/contexts/landlord-context.tsx",
                ],
                commit_message="feat(landlord): implement LandlordContext for property and tab state management",
            ),
            TaskSpec(
                task_id="WEB-057",
                repo="web",
                branch_name="feat/057-landlord-rooms-screen",
                task_file="tasks/landlord-rooms-screen.md",
                target_files=[
                    "src/components/landlord/landlord-rooms-screen.tsx",
                ],
                commit_message="feat(landlord): implement LandlordRoomsScreen with occupancy KPIs and drawer integration",
            ),
            TaskSpec(
                task_id="WEB-062",
                repo="web",
                branch_name="feat/062-landlord-pension-and-reviews",
                task_file="tasks/landlord-pension-and-reviews-screens.md",
                target_files=[
                    "src/components/landlord/landlord-pension-screen.tsx",
                    "src/components/landlord/landlord-reviews-screen.tsx",
                ],
                commit_message="feat(landlord): implement mobile pension profile editor and reviews inspection screens",
            ),
        ],
    ),
    5: WaveSpec(
        wave_number=5,
        description="Ensamblado Shell Móvil Propietario y Adaptación Responsiva Desktop",
        tasks=[
            TaskSpec(
                task_id="WEB-063",
                repo="web",
                branch_name="feat/063-landlord-shell-desktop-adaptation",
                task_file="tasks/landlord-shell-assembly-and-desktop-adaptation.md",
                target_files=[
                    "src/components/landlord/landlord-desktop-sidebar.tsx",
                    "src/components/landlord/landlord-desktop-header.tsx",
                    "src/components/shells/landlord-app-shell.tsx",
                ],
                commit_message="feat(landlord): assemble mobile shell and responsive desktop adaptation",
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
                if src_task.exists():
                    completed_dir = self.base_dir / task.repo / "tasks" / "completed"
                    completed_dir.mkdir(parents=True, exist_ok=True)
                    existing_numbers = []
                    for f in completed_dir.iterdir():
                        if f.is_file() and "_" in f.name and f.name[:3].isdigit():
                            existing_numbers.append(int(f.name[:3]))
                    next_idx = max(existing_numbers, default=0) + 1
                    dest_task = completed_dir / f"{next_idx:03d}_{src_task.name}"
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
