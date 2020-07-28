from unittest import mock

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from openwiden import vcs_clients
from openwiden.enums import OwnerType, VersionControlService, VisibilityLevel

DEFAULT_DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def compare_dt_strings(
    original: str,
    compare: str,
    original_format: str = DEFAULT_DATE_TIME_FORMAT,
    compare_format: str = DEFAULT_DATE_TIME_FORMAT,
    remove_microseconds: bool = False,
) -> bool:
    original_dt = timezone.datetime.strptime(original, original_format)
    compare_dt = timezone.datetime.strptime(compare, compare_format)

    if remove_microseconds:
        compare_dt = compare_dt.replace(microsecond=0)

    return original_dt == compare_dt


@pytest.mark.django_db
@pytest.mark.functional
@mock.patch("requests.sessions.Session.request")
def test_github(
    mock_request,
    create_api_client,
    create_mock_response,
    github_token_json,
    github_user_json,
    github_user_repositories_json,
):
    mock_responses = []

    # Create API client
    api_client = create_api_client()

    # Create mock token fetch response
    mock_responses.append(create_mock_response(github_token_json))

    # Create mock profile response
    mock_responses.append(create_mock_response(github_user_json))

    # Create mock avatar response
    mock_responses.append(create_mock_response(content=b"\0f"))

    # Create mock user repositories response
    mock_responses.append(create_mock_response(github_user_repositories_json))

    # Mock side effect for authlib requests
    mock_request.side_effect = mock_responses

    # Make request to auth complete view
    auth_complete_response = api_client.get(reverse("v1:auth-complete", kwargs={"vcs": VersionControlService.GITHUB}))

    # Test auth complete view response
    assert auth_complete_response.status_code == status.HTTP_200_OK
    assert list(auth_complete_response.data.keys()) == ["access", "refresh"]

    # Recreate API client with access token
    api_client = create_api_client(access_token=auth_complete_response.data["access"])

    # Make request to get user repositories
    user_repositories_response = api_client.get(reverse("api-v1:user-repositories-list"))

    # Test synced user repositories data
    assert user_repositories_response.data["count"] == len(github_user_repositories_json)
    for user_repository_data, raw_repository_data in zip(
        user_repositories_response.data["results"], github_user_repositories_json,
    ):
        assert user_repository_data["name"] == raw_repository_data["name"]
        assert user_repository_data["description"] == raw_repository_data["description"]
        assert user_repository_data["url"] == raw_repository_data["html_url"]
        assert user_repository_data["stars_count"] == raw_repository_data["stargazers_count"]
        assert user_repository_data["open_issues_count"] == raw_repository_data["open_issues_count"]
        assert user_repository_data["forks_count"] == raw_repository_data["forks_count"]
        assert user_repository_data["visibility"] == VisibilityLevel.public
        assert user_repository_data["is_added"] is False
        assert user_repository_data["vcs"] == VersionControlService.GITHUB
        assert compare_dt_strings(user_repository_data["updated_at"], raw_repository_data["updated_at"])
        assert compare_dt_strings(user_repository_data["created_at"], raw_repository_data["created_at"])
        if raw_repository_data["owner"]["type"] == vcs_clients.github.models.owner.OwnerType.ORGANIZATION:
            assert user_repository_data["owner"]["type"] == OwnerType.ORGANIZATION
            assert user_repository_data["owner"]["name"] == raw_repository_data["owner"]["login"]
        else:
            assert user_repository_data["owner"]["type"] == OwnerType.USER
            assert user_repository_data["owner"]["name"] == raw_repository_data["owner"]["login"]


@pytest.mark.django_db
@pytest.mark.functional
@mock.patch("requests.sessions.Session.request")
def test_gitlab(
    mock_request,
    create_api_client,
    create_mock_response,
    gitlab_token_json,
    gitlab_user_json,
    gitlab_user_repositories_json,
):
    api_client = create_api_client()
    mock_responses = []

    # Create mock token response
    mock_responses.append(create_mock_response(gitlab_token_json))

    # Create mock profile response
    mock_responses.append(create_mock_response(gitlab_user_json))

    # Create mock avatar response
    mock_responses.append(create_mock_response(content=b"\0f"))

    # Create mock repositories response
    mock_responses.append(create_mock_response(gitlab_user_repositories_json))

    # Mock requests
    mock_request.side_effect = mock_responses

    # Make auth complete request
    auth_complete_response = api_client.get(
        reverse("api-v1:auth-complete", kwargs={"vcs": VersionControlService.GITLAB})
    )

    # Test auth complete response
    assert auth_complete_response.status_code == status.HTTP_200_OK
    assert list(auth_complete_response.data.keys()) == ["access", "refresh"]

    # Recreate API client with access token
    api_client = create_api_client(access_token=auth_complete_response.data["access"])

    # Make request to get user repositories
    user_repositories_response = api_client.get(reverse("api-v1:user-repositories-list"))

    # Test synced user repositories data
    assert user_repositories_response.data["count"] == len(gitlab_user_repositories_json)
    for user_repository_data, raw_repository_data in zip(
        user_repositories_response.data["results"], gitlab_user_repositories_json,
    ):
        # Compare repository fields
        assert user_repository_data["name"] == raw_repository_data["name"]
        assert user_repository_data["description"] == raw_repository_data["description"]
        assert user_repository_data["url"] == raw_repository_data["web_url"]
        assert user_repository_data["stars_count"] == raw_repository_data["star_count"]
        assert user_repository_data["open_issues_count"] == raw_repository_data["open_issues_count"]
        assert user_repository_data["forks_count"] == raw_repository_data["forks_count"]
        assert user_repository_data["visibility"] == VisibilityLevel.public
        assert user_repository_data["is_added"] is False
        assert user_repository_data["vcs"] == VersionControlService.GITLAB

        # Compare date time fields
        assert compare_dt_strings(
            user_repository_data["updated_at"],
            raw_repository_data["last_activity_at"],
            compare_format="%Y-%m-%dT%H:%M:%S.%f%z",
            remove_microseconds=True,
        )
        assert compare_dt_strings(
            user_repository_data["created_at"],
            raw_repository_data["created_at"],
            compare_format="%Y-%m-%dT%H:%M:%S.%f%z",
            remove_microseconds=True,
        )

        # Compare owner
        if raw_repository_data["namespace"]["kind"] == vcs_clients.gitlab.models.repository.NamespaceKind.ORGANIZATION:
            assert user_repository_data["owner"]["type"] == OwnerType.ORGANIZATION
            assert user_repository_data["owner"]["name"] == raw_repository_data["namespace"]["name"]
        else:
            assert user_repository_data["owner"]["type"] == OwnerType.USER
            assert user_repository_data["owner"]["name"] == raw_repository_data["owner"]["username"]
