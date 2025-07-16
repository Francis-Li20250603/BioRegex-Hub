.PHONY: dev build test

dev:
	docker-compose up -d --build

build:
	docker-compose build

test:
	docker-compose exec api pytest /app/tests -v
	docker-compose exec web npm run test

logs:
	docker-compose logs -f

down:
	docker-compose down

migrate:
	docker-compose exec api python /app/scripts/init_db.py

celery:
	docker-compose exec celery celery -A celery_app worker --loglevel=info

prod:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
