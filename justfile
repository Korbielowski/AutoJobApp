install-deps: && instal-prod-deps install-dev-deps

install-dev-deps:
    uv sync --dev

install-prod-deps:
    uv sync

build-be:
    uv build

build-fe:
    bun run --cwd ./frontend openapi-typescript api/api.yaml -o api/api.ts
    bun run vinxi build
    rm -rf backend/_static && mkdir -p backend/_static && mv frontend/.output/public/* backend/_static
    echo "Frontend has been successfully built"

test-all: && test-be test-fe

test-be:
    uv run pytest -c tests/

test-fe:
