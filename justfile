install-deps: && install-prod-deps install-dev-deps

install-dev-deps:
    uv sync --dev

install-prod-deps:
    uv sync

build-be:
    uv build

build-fe:
    ./scripts/buildfrontend.sh

dev:
    ./scripts/dev.sh

test-all: && test-be test-fe

test-be:
    uv run pytest -c tests/

test-fe:
