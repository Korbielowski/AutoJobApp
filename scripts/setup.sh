#!/bin/sh
set -eu

command -v psql || { echo 'Psql/PostgreSQL not found, please install it first, in order to run the program.' ; exit 1; }
command -v weasyprint || { echo 'Weasyprint not found, please install it first, in order to run the program.' ; exit 1; }

sudo -u postgres psql -c "CREATE DATABASE autojobapp;" || { echo 'Database already created.'; }

if command -v uv; then
    uv sync --no-dev --frozen --compile-bytecode --no-cache
    uv run --no-sync --compile-bytecode playwright install --with-deps chromium
    if [ "$1" == "--run" ]; then
        uv run --no-sync --compile-bytecode fastapi run backend/app.py
    fi
else
    echo 'Uv not found, please install it first, as it is a recommended way of installing and running the program.'
    echo 'Do you want to continue without uv? [y/N]'
    read response
    if [ "$response" == "n" || "$response" == "no" || "$response" == "No" ]; then
        echo 'Installation cancelled.'
        exit 1
    fi
    echo 'Proceeding with installation without uv.'
    if command -v python3; then
        PYTHON=python3
    elif command -v python; then
        PYTHON=python
    else
        echo 'Python not found, please install it first, in order to run the program'
        exit 1
    fi
    $PYTHON -m venv .venv && . .venv/bin/activate
    $PYTHON -m pip install --requirement requirements.txt
    $PYTHON playwright install --with-deps chromium
    if [ "$1" == "--run" ]; then
        fastapi run backend/app.py
    fi
fi
