---
name: centralized-quality-gate
description: Procedimiento de compuerta centralizada de calidad para fusión de ramas, autofix Biome, verificación estática y suites de pruebas.
metadata:
  version: "1.0"
---

# Procedimiento de Compuerta Centralizada de Calidad

## Fases de Integración y Verificación
1. **Fusión de Ramas**:
   - Integrar cada rama de worker en la rama principal mediante `wt -C <repo> merge <branch-name>`.
   - Limpiar y remover el worktree temporal con `wt -C <repo> remove --force <branch-name> -D`.

2. **Ejecución de la Compuerta en una Sola Pasada**:
   - **Frontend (web)**:
     1. `pnpm run check`: Formateo y autofix con Biome.
     2. `pnpm exec tsc --noEmit`: Verificación estática de tipos.
     3. `pnpm run review`: Chequeo de reglas de linter y salida limpia.
     4. `pnpm vitest run`: Suite completa de pruebas unitarias.
   - **Backend (api)**:
     1. `pnpm run check`: Formateo y autofix con Biome.
     2. `pnpm run build`: Generación de cliente Prisma y compilación NestJS con SWC.
     3. `pnpm run review`: Chequeo de linter Biome.
     4. `pnpm test`: Suite de pruebas unitarias con Vitest.

3. **Ciclo de Archivo de Tareas**:
   - Mover las especificaciones de tareas aprobadas desde `tasks/<nombre>.md` hacia `tasks/completed/<NNN>_<nombre>.md` de forma cronológica.
   - Realizar commit de archivo: `chore(tasks): archive completed wave <N> tasks`.
