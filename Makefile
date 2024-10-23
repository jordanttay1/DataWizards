
.PHONY: tests pre-commit pytest

tests: pre-commit pytest
	@echo "\033[1;32mAll tests complete.\033[0m"

pre-commit:
	@echo "----------------------------------------"
	@echo "Running pre-commit..."
	@poetry run pre-commit run --all-files
	@echo "Pre-commit complete."
	@echo "----------------------------------------"

pytest:
	@echo "----------------------------------------"
	@echo "Running pytest..."
	@poetry run pytest
	@echo "Pytest complete."
	@echo "----------------------------------------"
