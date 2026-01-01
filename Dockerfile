FROM astral/uv:python3.12-bookworm-slim

WORKDIR /usr/src/autojobapp

COPY . .

RUN apt update && apt install --assume-yes weasyprint
RUN uv sync --no-dev --frozen --compile-bytecode --no-cache
RUN uv run --no-sync --compile-bytecode playwright install --with-deps chromium

EXPOSE 8000

ENTRYPOINT ["uv", "run", "--no-sync", "--compile-bytecode", "fastapi", "run", "backend/app.py"]
