PYTHON = uv run python3
MAIN = -m src
SRC = src/

all: install

uv.lock: pyproject.toml Makefile
	@echo "Installing dependencies using uv..."
	uv sync
	@touch uv.lock

install: uv.lock
	uv sync

run: install
	@echo "Running the program..."
	$(PYTHON) $(MAIN) maps/challenger/01_the_impossible_dream.txt

debug: install
	@echo "Starting debug mode..."
	$(PYTHON) -m pdb $(MAIN)

lint:
	@echo "Running standard linting..."
	uv run flake8 $(SRC)
	uv run mypy $(SRC) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@echo "Running strict linting..."
	uv run flake8 $(SRC)
	uv run mypy --strict $(SRC)

test:
	uv run python -m pytest tests/ -v

clean:
	@echo "Cleaning up..."
	rm -rf .mypy_cache \
	       .pytest_cache \

	find . -type d -name "__pycache__" -exec rm -rf {} +

.PHONY: all install run debug lint lint-strict clean profile