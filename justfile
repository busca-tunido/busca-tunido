set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]

default:
    @just --list

install:
    git submodule update --init --recursive
    pnpm -C web install
    pnpm -C api install

web-dev:
    pnpm -C web dev

api-dev:
    pnpm -C api start:dev

api-db:
    pnpm -C api run db:start

verify target="both":
    uv run --project orchestrator python orchestrator/main.py verify --target {{target}}

waves:
    uv run --project orchestrator python orchestrator/main.py list-waves

run-wave wave:
    uv run --project orchestrator python orchestrator/main.py run-wave {{wave}}

run-waves start="1" end="5":
    uv run --project orchestrator python orchestrator/main.py run-waves --start {{start}} --end {{end}}
