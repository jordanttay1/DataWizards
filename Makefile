
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

requirements:
	@echo "----------------------------------------"
	@echo "Generating requirements.txt..."
	@poetry export -f requirements.txt --without-hashes --output requirements.txt
	@echo "requirements.txt generated."
	@echo "----------------------------------------"

deploy: requirements
	@echo "----------------------------------------"
	@echo "Deploying GCLOUD"
	@gcloud app deploy
	@echo "Deployment complete."
	@echo "----------------------------------------"

serve:
	@echo "----------------------------------------"
	@echo "Running development server..."
	@poetry run gunicorn -w 4 -b 127.0.0.1:8080 dashapp.main:server
	@echo "Development server running."
	@echo "----------------------------------------"

serve-dev:
	@echo "----------------------------------------"
	@echo "Running development server..."
	@poetry run python dashapp/main.py
	@echo "Development server running."
	@echo "----------------------------------------"
