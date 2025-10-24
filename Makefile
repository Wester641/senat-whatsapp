.ONESHELL:

dev:
	uv run python manage.py runserver

migrate:
	uv run python manage.py migrate

compose-up:
	docker compose up --build -d

compose-down:
	docker compose down

compose-dev-up:
	docker compose -f docker-compose.dev.yml up --build

compose-dev-down:
	docker compose -f docker-compose.dev.yml down