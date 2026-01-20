# AutoJobApp
#
# @file
# @version 0.1
.PHONY: py
# Insall Python dependencies
py:
	uv pip install --group=dev -e .

.PHONY: test
test:
	uv run pytest -s .

.PHONY: build
# Build the Python backend
build:
	uv build
