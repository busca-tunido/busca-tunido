---
name: token-efficient-coding
description: Directrices de implementación de código eficiente: tipado estricto, sin comentarios, sin comandos pesados y commits convencionales.
metadata:
  version: "1.0"
---

# Directrices de Implementación Token-Efficient

## Reglas de Implementación en Worktrees
1. **Límites de Archivos Exclusivos**:
   - Trabajar únicamente sobre la lista explícita de Target Files asignada a la tarea.
   - Prohibido modificar o crear archivos fuera del alcance definido.

2. **Comandos Prohibidos en Workers**:
   - NUNCA ejecutar: `pnpm build`, `tsc`, `nest build`, `biome check`, `git stash`, o `git reset`.
   - Estas validaciones corresponden centralizadamente a la compuerta de calidad en la fase de integración.

3. **Tipado Estricto y Convenciones de Código**:
   - Utilizar tipado estricto estándar en TypeScript y Python. Prohibido el uso de `any`.
   - No escribir comentarios dentro del código a menos que el usuario lo solicite explícitamente.
   - Respetar el nombre de marca: `BuscaTuNido` (PascalCase, una sola palabra).

4. **Staging y Commit**:
   - Ejecutar únicamente: `git add <archivo1> <archivo2> ...`
   - Realizar un commit convencional en una sola línea (ej. `feat(landlord): implement room item card`).
   - Salir inmediatamente tras el commit para liberar el worktree.
