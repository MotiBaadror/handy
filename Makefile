.PHONY: run install lint format clean

run:
	uv run python main.py

install:
	uv sync

lint:
	uv run ruff check .

format:
	uv run ruff format .

clean:
	rm -rf .venv __pycache__ .ruff_cache
