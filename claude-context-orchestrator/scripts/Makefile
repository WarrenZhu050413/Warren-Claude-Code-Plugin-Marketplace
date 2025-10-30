# snippets-cli Makefile - uv-based automation

UV := uv
SHELL_TYPE := $(shell basename $$SHELL)

.DEFAULT_GOAL := install

.PHONY: help install dev test lint format clean

help:
	@echo "snippets-cli Makefile (uv-based)"
	@echo ""
	@echo "Available targets:"
	@echo "  make install    - Install globally (always rebuilds from scratch)"
	@echo "  make dev        - Setup dev environment (use 'uv run snippets')"
	@echo "  make test       - Run pytest test suite"
	@echo "  make lint       - Run ruff linting"
	@echo "  make format     - Format code with ruff"
	@echo "  make clean      - Remove build artifacts"
	@echo ""
	@echo "Development workflow:"
	@echo "  Recommended: make dev + uv run snippets  (changes reflect immediately)"
	@echo "  Alternative: make install  (reinstall after each change)"

install: clean
	@echo "📦 Installing snippets-cli globally..."
	@echo "   Cleaning stale build artifacts first..."
	$(UV) tool install --force .
	@echo "✅ Installed globally!"
	@echo ""
	@echo "⚠️  Note: After code changes, run 'make install' again to rebuild."
	@echo "   Or use 'make dev' + 'uv run snippets' for instant changes."

dev:
	@echo "📦 Installing locally with dev dependencies (editable)..."
	$(UV) sync --all-extras
	@echo "✅ Dev environment ready (use 'uv run snippets' or 'uv run pytest')"

test:
	@echo "🧪 Running tests..."
	$(UV) run pytest -v
	@echo "✅ Tests complete"

lint:
	@echo "🔍 Linting..."
	$(UV) run ruff check .

format:
	@echo "✨ Formatting..."
	$(UV) run ruff format .

clean:
	@echo "🧹 Cleaning..."
	rm -rf build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Clean complete"
