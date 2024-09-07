
.PHONY: tests pre-commit

tests: pre-commit
	@echo "\033[1;32mAll tests complete.\033[0m"

pre-commit:
	@echo "----------------------------------------"
	@echo "Running pre-commit..."
	@poetry run pre-commit run --all-files
	@echo "Pre-commit complete."
	@echo "----------------------------------------"
