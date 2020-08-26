from typing import List

import pytest
from django.core.cache import cache
from django.urls import reverse
from pytest_cases import parametrize, parametrize_with_cases
from rest_framework import status

from openwiden.repositories.enums import RepositoryState

REPOSITORY_STATE_VALUES_EXCLUDE_ADDED = [value for value in RepositoryState.values if value != RepositoryState.ADDED]


def case_no_repositories() -> List[str]:
    return []


@parametrize("state", REPOSITORY_STATE_VALUES_EXCLUDE_ADDED)
def case_only_not_added_repository(create_repository, state: str) -> List[str]:
    create_repository(state=state)
    return []


@parametrize("state", REPOSITORY_STATE_VALUES_EXCLUDE_ADDED)
def case_only_one_added_repository(create_repository, state: str) -> List[str]:
    vue_repository_languages = {"Docker": 5, "JavaScript": 35, "Vue": 60}
    create_repository(state=state)
    create_repository(programming_languages=vue_repository_languages, state=RepositoryState.ADDED)
    return sorted(vue_repository_languages.keys())


@pytest.mark.functional
@pytest.mark.django_db
@parametrize_with_cases("expected_programming_languages", cases=".")
def test_run(create_api_client, expected_programming_languages: List[str]):
    # Clear view cache
    cache.clear()

    # Create api client and repositories
    api_client = create_api_client()

    # Make request
    response = api_client.get(reverse("api-v1:programming_languages"))

    # Test
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_programming_languages
