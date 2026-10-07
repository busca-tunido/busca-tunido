---
name: worktree-orchestration
description: Metodología para descomponer requerimientos en olas DAG con conjuntos de archivos disjuntos usando worktrunk (wt).
metadata:
  version: "1.0"
---

# Metodología de Orquestación de Worktrees y Olas DAG

## Principios Fundamentales
1. **Partición Estricta de Archivos**:
   - Cada tarea paralela debe tener un conjunto de archivos objetivo estrictamente disjunto.
   - Para dos tareas A y B en la misma ola: Files(A) ∩ Files(B) = ∅.
   - Los archivos de integración compartidos (como layout.tsx o app.module.ts) quedan reservados exclusivamente para la fase de integración.

2. **Gestión de Worktrees con Worktrunk (wt)**:
   - Los worktrees se alojan obligatoriamente en el directorio ignorado por git `trees/` (`trees/<repo>.<branch-name>`), configurado mediante `orchestrator/config/wt.toml` (`worktree-path = "{{ repo_path }}/../trees/{{ repo }}.{{ branch | sanitize }}"`).
   - Crear worktree aislado en `trees/`: `wt -C <repo> --config orchestrator/config/wt.toml switch --create <branch-name>` (o `just wt-switch <repo> <branch-name>`).
   - Inspeccionar worktrees activos: `wt -C <repo> --config orchestrator/config/wt.toml list` (o `just worktrees <repo>`).
   - Fusionar rama completada: `wt -C <repo> merge <branch-name>` (o `just wt-merge <repo> <branch-name>`).
   - Limpieza y eliminación: `wt -C <repo> --config orchestrator/config/wt.toml remove --force <branch-name> -D` (o `just wt-remove <repo> <branch-name>`).

3. **Planificación de Olas**:
   - Agrupar hasta 4 tareas en paralelo por ola para maximizar el throughput sin degradar el contexto.
   - Resolver dependencias lógicas: las tareas de backend requeridas deben ejecutarse en olas previas a los componentes de frontend que las consumen.
