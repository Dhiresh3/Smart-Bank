# ------------------------------------------------------------
# SmartBank Project Makefile
# ------------------------------------------------------------
# Primary entry point (editable via USER_RESPONSE_ENTRY)
ENTRY_POINT ?= bank_logic.py

# Python interpreter & virtual environment settings
PYTHON := python
PIP := pip
VENV_DIR := .venv

# ------------------------------------------------------------
# Helper Targets
# ------------------------------------------------------------
.PHONY: all install lint health check run clean

all: install lint health

# Install dependencies (creates venv if missing)
install: $(VENV_DIR)\\Scripts\\activate
	@echo "✅ Dependencies installed"

$(VENV_DIR)\\Scripts\\activate:
	@$(PYTHON) -m venv $(VENV_DIR)
	@$(VENV_DIR)\\Scripts\\pip install --upgrade pip
	@if [ -f requirements.txt ]; then \
		$(VENV_DIR)\\Scripts\\pip install -r requirements.txt; \
	else \
		$(VENV_DIR)\\Scripts\\pip install -r <(pip freeze); \
	fi

# Linting with flake8 (optional – user can disable by setting LINT=false)
LINT ?= true
lint:
	@if [ "$(LINT)" = "true" ]; then \
		$(VENV_DIR)\\Scripts\\flake8 . --max-line-length=120; \
	else \
		echo "⚠️ Linting skipped (LINT=false)"; \
	fi

# Run a lightweight health‑check script (see health_check.py)
health check: health_check.py
	@$(VENV_DIR)\\Scripts\\python health_check.py

# Run the main application
run:
	@$(VENV_DIR)\\Scripts\\python $(ENTRY_POINT)

# Clean virtual environment and pyc files
clean:
	rm -rf $(VENV_DIR) __pycache__ *.pyc
