BLUE  := \033[1;36m
RESET := \033[0m


install:
	@echo "$(BLUE)Running uv sync...${RESET}"
	@echo ""
	@uv sync
 
run:
	uv run python -m src
 
debug:
	uv run python -m pdb -m src
 
lint:
	@echo "$(BLUE)Running flake8 and mypy...${RESET}"
	@uv run flake8 src/*.py
	@uv run mypy src/*.py --strict --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
 
clean:
	@rm -rf src/__pycache__
	@rm -rf llm_sdk/__pycache__

.PHONY: install run debug lint clean
