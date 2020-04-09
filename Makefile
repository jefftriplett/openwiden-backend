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

### Fixtures
_load_fixture:
	@make manage c="loaddata $(fixture)"
load_fixtures:
	@make _load_fixture fixture="version_control_services.json"

# Code quality
flake8:
	$(WEB_CONTAINER) flake8

black:
	$(WEB_CONTAINER) black .

black_check:
	$(WEB_CONTAINER) black --check .

# Tests
with_test_settings:
	DJANGO_CONFIGURATION=Test $(WEB_CONTAINER) $(c)

test:
	@make with_test_settings c="coverage run manage.py test --settings=config.settings.test"

test_cov:
	@make with_test_settings c="coverage erase"
	@make test
	@make with_test_settings c="coverage report -m"
	@make with_test_settings c="coverage html"

run_tests:
	@make test
	@make black_check
	@make flake8
	@make with_test_settings c="coverage xml"
	@make with_test_settings c="codecov"
