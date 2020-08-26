from typing import List, Set, Tuple, Union

import pytest
from django.urls import reverse
from pytest_cases import parametrize, parametrize_with_cases
from rest_framework import status

from openwiden.repositories import models
from openwiden.repositories.enums import RepositoryState

ProgrammingLanguages = Union[List[str], Set[str]]
TestData = Tuple[ProgrammingLanguages, List[models.Repository]]


def case_filter_with_one_programming_language(create_repository) -> TestData:
    repositories = [create_repository(state=RepositoryState.ADDED)]
    return list(repositories[0].programming_languages.keys()), repositories


@parametrize("programming_languages", [["Python", "Vue"], ["JavaScript", "Docker"], ["Docker", "Python"],])
def case_filter_with_multiple_programming_languages(create_repository, programming_languages: List[str]) -> TestData:
    vue_repository_languages = {"Docker": 5, "JavaScript": 35, "Vue": 60}
    python_repository_languages = {"Python": 60, "Docker": 5, "JavaScript": 35}
    repositories = [
        create_repository(
            programming_languages=vue_repository_languages, state=RepositoryState.ADDED, open_issues_count=10
        ),
        create_repository(
            programming_languages=python_repository_languages, state=RepositoryState.ADDED, open_issues_count=5
        ),
    ]

    return programming_languages, repositories


def case_filter_with_no_programming_languages(create_repository) -> TestData:
    return [], [create_repository(state=RepositoryState.ADDED)]


@pytest.mark.functional
@pytest.mark.django_db
@parametrize_with_cases("programming_languages, expected_repositories", cases=".")
def test_run(
    create_api_client, programming_languages: ProgrammingLanguages, expected_repositories: List[models.Repository],
):
    # Create api client
    api_client = create_api_client()

    # Format programming languages
    if len(programming_languages) == 0:
        programming_languages = ""
    elif len(programming_languages) == 1:
        programming_languages = programming_languages[0]
    else:
        programming_languages = ",".join(programming_languages)

    # Make filter request
    url = f'{reverse("api-v1:repository-list")}?programming_languages={programming_languages}'
    response = api_client.get(url)

    # Test
    assert response.status_code == status.HTTP_200_OK
    response_ids = [repository["id"] for repository in response.json()["results"]]
    expected_ids = [str(repository.id) for repository in expected_repositories]
    assert response_ids == expected_ids
