.PHONY: init run lint lint-fix ty clean docker-build docker-run

# Initialize project and install dependencies
init:
	uv sync

# Run the tracker script
run:
	uv run python src/main.py

# Run ruff linter
lint:
	uv run ruff check src/
	uv run ruff format --check src/

# Run ruff linter and fix issues
lint-fix:
	uv run ruff check --fix src/
	uv run ruff format src/

# Run ty type checker
ty:
	uv run ty check src/

# Clean generated files
clean:
	rm -rf .venv __pycache__ src/__pycache__ .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Build Docker image (works with both docker and podman)
docker-build:
	podman build -t pchome-tracker:latest .

# Run in Docker container (works with both docker and podman)
docker-run:
	podman run --rm --env-file .env -v "$$(pwd)/db:/app/db:Z" pchome-tracker:latest
