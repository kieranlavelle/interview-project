

setup:
	@echo "Setting up the project..."
	@echo "Installing dependencies..."
	poetry install
	poetry run pre-commit install

unit-test: setup
	docker compose up db -d
	@echo "Giving the database 10 seconds to start..."
	sleep 10
	@echo "Running unit tests..."
	poetry run pytest
	docker compose down
	docker compose down --volumes

db-up:
	docker compose up db -d

db-down:
	docker compose down

app-up:
	docker compose down --volumes
	export DOCKER_DEFAULT_PLATFORM=linux/amd64 && docker compose up --build -d

app-down:
	docker compose down
	docker compose down --volumes
