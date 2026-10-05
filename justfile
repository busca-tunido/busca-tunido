set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]

default:
    @just --list

install:
    git submodule update --init --recursive
    pnpm -C web install
    pnpm -C api install

build target="both":
    @if ("{{target}}" -eq "both" -or "{{target}}" -eq "api") { pnpm -C api run build }
    @if ("{{target}}" -eq "both" -or "{{target}}" -eq "web") { pnpm -C web run build }

typecheck target="both":
    @if ("{{target}}" -eq "both" -or "{{target}}" -eq "api") { pnpm -C api exec tsc --noEmit -p tsconfig.build.json }
    @if ("{{target}}" -eq "both" -or "{{target}}" -eq "web") { pnpm -C web exec tsc --noEmit }

check target="both":
    @if ("{{target}}" -eq "both" -or "{{target}}" -eq "api") { pnpm -C api run check }
    @if ("{{target}}" -eq "both" -or "{{target}}" -eq "web") { pnpm -C web run check }

review target="both":
    @if ("{{target}}" -eq "both" -or "{{target}}" -eq "api") { pnpm -C api run review }
    @if ("{{target}}" -eq "both" -or "{{target}}" -eq "web") { pnpm -C web run review }

test target="both":
    @if ("{{target}}" -eq "both" -or "{{target}}" -eq "api") { pnpm -C api run test }
    @if ("{{target}}" -eq "both" -or "{{target}}" -eq "web") { pnpm -C web exec vitest run }

postman:
    pnpm -C api generate:postman

web-dev:
    pnpm -C web dev

api-dev:
    pnpm -C api start:dev

api-db:
    pnpm -C api run db:start

seed:
    pnpm -C api run db:seed

verify target="both":
    uv run --project orchestrator python orchestrator/main.py verify --target {{target}}

discover repo="both":
    uv run --project orchestrator python orchestrator/main.py discover --repo {{repo}}

run-flow:
    uv run --project orchestrator python orchestrator/main.py run-flow

plan requirement="":
    uv run --project orchestrator python orchestrator/main.py plan {{ if requirement != "" { "-r \"" + requirement + "\"" } else { "" } }}

worktrees repo="web":
    uv run --project orchestrator python orchestrator/main.py worktrees --repo {{repo}}

new-task repo="web" slug="" title="":
    uv run --project orchestrator python orchestrator/main.py new-task --repo {{repo}} --slug {{slug}} --title "{{title}}"

heal target="both" retries="2":
    uv run --project orchestrator python orchestrator/main.py heal --target {{target}} --retries {{retries}}

sync-submodules:
    uv run --project orchestrator python orchestrator/main.py sync-submodules

archive repo="web" task="":
    uv run --project orchestrator python orchestrator/main.py archive --repo {{repo}} --task {{task}}
