# snippets-cli Makefile - uv-based automation

UV := uv
SHELL_TYPE := $(shell basename $$SHELL)

.DEFAULT_GOAL := install

.PHONY: help install install-editable dev test lint format clean install-completion

help:
	@echo "snippets-cli Makefile (uv-based)"
	@echo ""
	@echo "Available targets:"
	@echo "  make install             - Install globally (production, rebuilds each time)"
	@echo "  make install-editable    - Install globally in editable mode (changes instant)"
	@echo "  make dev                 - Setup dev environment (use 'uv run snippets')"
	@echo "  make test                - Run pytest test suite"
	@echo "  make lint                - Run ruff linting"
	@echo "  make format              - Format code with ruff"
	@echo "  make clean               - Remove build artifacts"
	@echo "  make install-completion  - Setup shell completion"
	@echo ""
	@echo "Development workflow (choose one):"
	@echo "  Recommended: make install-editable  (global install, changes instant)"
	@echo "  Alternative: make dev + uv run snippets  (local, need 'uv run' prefix)"

install: clean
	@echo "📦 Installing snippets-cli globally (production mode)..."
	@echo "   Cleaning UV cache and build artifacts..."
	$(UV) cache clean --force
	$(UV) tool install --force .
	@echo "✅ Installed globally!"
	@echo ""
	@echo "⚠️  Note: After code changes, run 'make install' again to rebuild."
	@echo "   Or use 'make install-editable' for instant changes."

install-editable: clean
	@echo "📦 Installing snippets-cli globally (editable mode)..."
	@echo "   Cleaning UV cache and build artifacts..."
	$(UV) cache clean --force
	$(UV) tool install --force --editable .
	@echo "✅ Installed globally in editable mode!"
	@echo ""
	@echo "✨ Changes to Python files will take effect immediately (no reinstall needed)"

dev:
	@echo "📦 Installing locally with dev dependencies (editable)..."
	$(UV) sync --all-extras
	@echo "✅ Dev environment ready (use 'uv run snippets' or 'uv run pytest')"

test:
	@echo "🧪 Running tests..."
	$(UV) run pytest --cov=snippets --cov-report=term-missing
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
	$(UV) run snippets --install-completion $(SHELL_TYPE)
	@echo "✅ Restart shell: exec $$SHELL"
