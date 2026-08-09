BLUE  := \033[1;36m
GREEN := \033[1;32m
RESET := \033[0m


install:
	@echo "$(BLUE)Running uv sync...${RESET}"
	@echo ""
	@uv sync
 
run:
	@uv run python -m src
 
debug:
	@uv run python -m pdb -m src
 
lint:
	@echo "$(BLUE)Running flake8 and mypy...${RESET}"
	@uv run flake8 src/*.py
	@uv run mypy src/*.py --strict --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
 
clean:
	@echo "$(BLUE)Cleaning cache in src and llm_dsk...${RESET}"
	@rm -rf src/__pycache__
	@rm -rf llm_sdk/__pycache__
	@rm -rf .mypy_cache
	@echo "$(GREEN)Done!${RESET}"


.PHONY: install run debug lint clean
