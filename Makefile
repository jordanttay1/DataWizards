
.PHONY: tests pre-commit pytest deploy serve serve-dev

submission: submission_dir README.txt requirements.txt DOC CODE
	@echo "----------------------------------------"
	@echo "Creating team135final.zip..."
	@(cd submission && zip -r ../team135final.zip .)
	@echo "team135final.zip created."
	@echo "----------------------------------------"

submission_dir:
	@mkdir -p submission

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

requirements.txt: pyproject.toml
	@echo "----------------------------------------"
	@echo "Generating requirements.txt..."
	@poetry export -f requirements.txt --without-hashes --output requirements.txt
	@echo "requirements.txt generated."
	@echo "----------------------------------------"

deploy: requirements.txt
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

README.txt: submission_dir README.md
	@echo "----------------------------------------"
	@echo "Generating README.txt..."
	@cp README.md submission/README.txt
	@echo "README.txt generated."
	@echo "----------------------------------------"

DOC: DOC/team135report.pdf DOC/team135poster.pdf

DOC/team135report.pdf: submission_dir
	@echo "----------------------------------------"
	@echo "Generating report pdf..."
	@soffice --headless --convert-to pdf team135report.docx --outdir submission/DOC
	@echo "PDF generated."
	@echo "----------------------------------------"

DOC/team135poster.pdf: submission_dir
	@echo "----------------------------------------"
	@echo "Generating poster pdf..."
	@soffice --headless --convert-to pdf team135poster.pptx --outdir submission/DOC
	@echo "PDF generated."
	@echo "----------------------------------------"

CODE: submission_dir
	@echo "----------------------------------------"
	@echo "Copying code files to submission/CODE..."
	@rsync -av --delete --prune-empty-dirs --exclude=".venv/" --exclude='tests/' --exclude='docs/' --exclude='submission' --include='*/' --include='*.py' --include='*.ipynb' --include='*.md' --include='*.toml' --include='poetry.lock' --include='Makefile' --include='requirements.txt' --exclude='*'  . submission/CODE
	@echo "Code files copied."
	@echo "----------------------------------------"
