.PHONY: run chat dev install lint format clean

run:
	uv run python main.py

chat:
	uv run python client.py

dev:
	uv run watchfiles "python client.py" src/ client.py

install:
	uv sync

lint:
	uv run ruff check .

format:
	uv run ruff format .

clean:
	rm -rf .venv __pycache__ .ruff_cache
