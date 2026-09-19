set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]

default:
    @just --list

install:
    git submodule update --init --recursive
    pnpm -C web install
    pnpm -C api install

build:
    pnpm -C api run build
    pnpm -C web run build

web-dev:
    pnpm -C web dev

api-dev:
    pnpm -C api start:dev

api-db:
    pnpm -C api run db:start

seed:
    pnpm -C api run db:seed

test:
    pnpm -C api run test
    pnpm -C web run test

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
