WEB_CONTAINER=docker-compose run --rm web
BASE_COMPOSE_FILES=docker-compose.yml
LOCAL_COMPOSE_FILES=$(BASE_COMPOSE_FILES) docker-compose.develop.yml
PRODUCTION_COMPOSE_FILES=$(BASE_COMPOSE_FILES)


# Containers
web:
	$(WEB_CONTAINER) $(c)


# Docker
down:
	@docker-compose down --remove-orphans

up:
	@make down && \
		docker-compose $(foreach file, $($(COMPOSE_FILES)), -f $(file)) up -d --build

local_up:
	@make up COMPOSE_FILES=LOCAL_COMPOSE_FILES

production_up:
	@make up COMPOSE_FILES=PRODUCTION_COMPOSE_FILES


# Django
manage:
	@make web c="python manage.py $(c)"

### Migrations
mm:
	@make manage c=makemigrations
migrate:
	@make manage c=migrate


# Code quality
flake8:
	$(WEB_CONTAINER) flake8

black:
	$(WEB_CONTAINER) black .

black_check:
	$(WEB_CONTAINER) black --check .

# Tests
test:
	$(WEB_CONTAINER) python manage.py test

run_tests:
	@make test
	@make black_check
	@make flake8
