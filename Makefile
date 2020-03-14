BASE_COMPOSE_FILES=docker-compose.yml
#LOCAL_COMPOSE_FILES=$(BASE_COMPOSE_FILES) docker-compose.develop.yml
#TEST_COMPOSE_FILES=$(BASE_COMPOSE_FILES) docker-compose.test.yml
#STAGING_COMPOSE_FILES=$(BASE_COMPOSE_FILES) docker-compose.staging.yml
#PRODUCTION_COMPOSE_FILES=$(BASE_COMPOSE_FILES) docker-compose.production.yml

COMPOSE_FILES=BASE_COMPOSE_FILES

WEB_CONTAINER=docker-compose $(foreach file, $($(COMPOSE_FILES)), -f $(file)) run --rm web

# Containers
web:
	$(WEB_CONTAINER) $(c)

# Docker
docker-compose:
	docker-compose $(foreach file, $($(COMPOSE_FILES)), -f $(file)) $(command)

up:
	@make docker-compose command="up -d --build"

down:
	@make docker-compose command="down --remove-orphans"

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
	DJANGO_CONFIGURATION=Test $(WEB_CONTAINER) python manage.py test --settings=config.settings.test

run_tests:
	@make test
	@make black_check
	@make flake8
