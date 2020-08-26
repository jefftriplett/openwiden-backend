from unittest import mock

import pytest
from django.urls import reverse
from rest_framework import status

from openwiden.enums import VersionControlService


@pytest.mark.functional
@pytest.mark.django_db
@mock.patch("requests.sessions.Session.request")
@pytest.mark.parametrize("is_organization_repository", [True, False])
def test_github(
    mock_request,
    user,
    create_api_client,
    create_vcs_account,
    create_repository,
    create_mock_response,
    github_organization_repository_json,
    github_repository_json,
    github_repository_languages_json,
    github_repository_issues_json,
    github_webhook_create_json,
    github_organization_json,
    github_user_membership_for_organization_json,
    is_organization_repository: bool,
):
    api_client = create_api_client(user=user)
    vcs_account = create_vcs_account(user=user, vcs=VersionControlService.GITHUB)
    repository = create_repository(vcs=VersionControlService.GITHUB, owner=vcs_account, organization=None)
    mock_responses = [
        # Create mock repository response
        create_mock_response(
            github_organization_repository_json if is_organization_repository else github_repository_json
        ),
        # Create mock languages response
        create_mock_response(github_repository_languages_json),
    ]

    if is_organization_repository:
        mock_responses += [
            # Create mock organization response
            create_mock_response(github_organization_json),
            # Create mock user membership check for organization
            create_mock_response(github_user_membership_for_organization_json),
        ]

    mock_responses += [
        # Create mock repository issues response
        create_mock_response(github_repository_issues_json),
        # Create mock webhook create response
        create_mock_response(github_webhook_create_json),
    ]

    # Mock responses
    mock_request.side_effect = mock_responses

    # Make add request
    response = api_client.post(reverse("api-v1:user-repository-add", kwargs={"id": str(repository.id)}))

    # Test response
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"detail": "ok"}


@pytest.mark.functional
@pytest.mark.django_db
@mock.patch("requests.sessions.Session.request")
@pytest.mark.parametrize("is_organization_repository", [True, False])
def test_gitlab(
    mock_request,
    user,
    create_api_client,
    create_vcs_account,
    create_repository,
    create_mock_response,
    gitlab_repository_json,
    gitlab_organization_repository_json,
    gitlab_repository_languages_json,
    gitlab_repository_issues_json,
    gitlab_webhook_create_json,
    gitlab_organization_json,
    gitlab_organization_member_json,
    is_organization_repository: bool,
):
    api_client = create_api_client(user=user)
    vcs_account = create_vcs_account(user=user, vcs=VersionControlService.GITLAB)
    repository = create_repository(vcs=VersionControlService.GITLAB, owner=vcs_account, organization=None)
    mock_responses = [
        # Create mock repository
        create_mock_response(
            gitlab_organization_repository_json if is_organization_repository else gitlab_repository_json
        ),
        # Mock programming languages response
        create_mock_response(gitlab_repository_languages_json),
    ]

    if is_organization_repository:
        mock_responses += [
            # Mock organization response
            create_mock_response(gitlab_organization_json),
            # Mock organization membership check
            create_mock_response(gitlab_organization_member_json),
        ]

    mock_responses += [
        # Mock issues response
        create_mock_response(gitlab_repository_issues_json),
        # Mock webhook create response
        create_mock_response(gitlab_webhook_create_json),
    ]

    # Mock request
    mock_request.side_effect = mock_responses

    # Make add request
    response = api_client.post(reverse("v1:user-repository-add", kwargs={"id": str(repository.id)}))

    # Test response
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"detail": "ok"}
