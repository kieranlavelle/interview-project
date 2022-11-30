

unit-test:
	docker compose up db -d
	sleep 5
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