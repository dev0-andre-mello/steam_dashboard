# Activate venv and run application
run:
	. venv/bin/activate && python app.python

# Install dependencies
install:
	pip install -r requirements.txt

# Update requirements file
freeze:
	pip freeze > requirements.txt

# Code formating
format:
	black .

# Execute lint with flake8
lint:
	@flake8 features

# Tests
test:
	PYTHONPATH=. pytest