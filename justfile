set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]

export WORKTRUNK_CONFIG_PATH := justfile_directory() + "/orchestrator/config/wt.toml"

default:
    @just --list

install:
    git submodule update --init --recursive
    pnpm -C web install
    pnpm -C api install

typecheck target="both":
    @if ("{{target}}" -in @("both", "api")) { pnpm -C api exec tsc --noEmit -p tsconfig.build.json }
    @if ("{{target}}" -in @("both", "web")) { pnpm -C web exec tsc --noEmit }

check target="both":
    @if ("{{target}}" -in @("both", "api")) { pnpm -C api run check }
    @if ("{{target}}" -in @("both", "web")) { pnpm -C web run check }

test target="both":
    @if ("{{target}}" -in @("both", "api")) { pnpm -C api run test }
    @if ("{{target}}" -in @("both", "web")) { pnpm -C web exec vitest run }

openapi:
    pnpm -C api run build
    pnpm -C api run openapi:export
    pnpm -C web exec openapi-typescript src/lib/openapi.json -o src/lib/api-schema.d.ts --immutable --default-non-nullable
    pnpm -C web exec biome format --write src/lib/api-schema.d.ts src/lib/openapi.json

dev-web:
    pnpm -C web dev

dev-api:
    pnpm -C api start:dev

seed:
    pnpm -C api run db:seed

verify target="both":
    uv run --project orchestrator python orchestrator/main.py verify --target {{target}}

run-flow:
    uv run --project orchestrator python orchestrator/main.py run-flow

discover repo="both":
    uv run --project orchestrator python orchestrator/main.py discover --repo {{repo}}

plan requirement="":
    uv run --project orchestrator python orchestrator/main.py plan {{ if requirement != "" { "-r \"" + requirement + "\"" } else { "" } }}

new-task repo="web" slug="" title="":
    uv run --project orchestrator python orchestrator/main.py new-task --repo {{repo}} --slug {{slug}} --title "{{title}}"

archive repo="web" task="":
    uv run --project orchestrator python orchestrator/main.py archive --repo {{repo}} --task {{task}}
