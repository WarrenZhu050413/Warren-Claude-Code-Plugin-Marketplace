# gmaillm Makefile - uv-based automation

UV := uv
SHELL_TYPE := $(shell basename $$SHELL)

.DEFAULT_GOAL := install

.PHONY: help install dev test lint format clean install-completion

help:
	@echo "gmaillm Makefile (uv-based)"
	@echo ""
	@echo "Available targets:"
	@echo "  make install             - Install gmaillm globally with uv tool install"
	@echo "  make dev                 - Install with dev dependencies (local)"
	@echo "  make test                - Run pytest test suite"
	@echo "  make lint                - Run ruff linting"
	@echo "  make format              - Format code with ruff"
	@echo "  make clean               - Remove build artifacts"
	@echo "  make install-completion  - Setup shell completion"

install:
	@echo "📦 Installing gmaillm globally with uv tool install..."
	$(UV) tool install --force --editable .
	@echo "✅ Installed globally! Try: gmail --help"

dev:
	@echo "📦 Installing with dev dependencies..."
	$(UV) sync --all-extras
	@echo "✅ Dev environment ready"

test:
	@echo "🧪 Running tests..."
	$(UV) run pytest --cov=gmaillm --cov-report=term-missing
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
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Clean complete"

install-completion:
	@echo "🎯 Installing completion for $(SHELL_TYPE)..."
	$(UV) run gmail --install-completion $(SHELL_TYPE)
	@echo "✅ Restart shell: exec $$SHELL"
