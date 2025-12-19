command -v curl || { echo 'curl command not found, you must install it' ; exit 1; }
command -v uv || { curl -LsSf https://astral.sh/uv/install.sh | sh; }

uv sync
