install-deps:
    instal-prod-deps
    install-dev-deps

install-dev-deps:
    uv sync --dev

install-prod-deps:
    uv sync

build-be:
    uv build

build-fe:
    bun run --cwd ./frontend openapi-typescript api/api.yaml -o api/api.ts

test-all:
    test-be
    test-fe

test-be:
    uv run pytest -c tests/

test-fe:
