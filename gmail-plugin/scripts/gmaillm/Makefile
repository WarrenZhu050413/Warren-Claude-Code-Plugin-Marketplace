# gmaillm Makefile - uv-based automation

UV := uv
SHELL_TYPE := $(shell basename $$SHELL)

.DEFAULT_GOAL := install

.PHONY: help install dev test lint format clean install-completion

help:
	@echo "gmaillm Makefile (uv-based)"
	@echo ""
	@echo "Available targets:"
	@echo "  make install             - Install globally (always rebuilds from scratch)"
	@echo "  make dev                 - Setup dev environment (use 'uv run gmail')"
	@echo "  make test                - Run pytest test suite"
	@echo "  make lint                - Run ruff linting"
	@echo "  make format              - Format code with ruff"
	@echo "  make clean               - Remove build artifacts"
	@echo "  make install-completion  - Setup shell completion"
	@echo ""
	@echo "Development workflow:"
	@echo "  Recommended: make dev + uv run gmail  (changes reflect immediately)"
	@echo "  Alternative: make install  (reinstall after each change)"

install: clean
	@echo "📦 Installing gmaillm globally..."
	@echo "   Cleaning stale build artifacts first..."
	$(UV) tool install --force .
	@echo "✅ Installed globally!"
	@echo ""
	@echo "⚠️  Note: After code changes, run 'make install' again to rebuild."
	@echo "   Or use 'make dev' + 'uv run gmail' for instant changes."

dev:
	@echo "📦 Installing locally with dev dependencies (editable)..."
	$(UV) sync --all-extras
	@echo "✅ Dev environment ready (use 'uv run gmail' or 'uv run pytest')"

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
