FROM astral/uv:python3.12-bookworm-slim

WORKDIR /usr/src/autoapply

COPY . .

RUN uv sync --no-dev --frozen --compile-bytecode --no-cache
RUN apt update && apt install --assume-yes weasyprint

EXPOSE 8000

ENTRYPOINT ["uv", "run", "fastapi", "run", "backend/app.py"]
