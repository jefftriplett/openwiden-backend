from copy import deepcopy
from unittest import mock

import pytest
from django.urls import reverse
from django.utils import timezone

from openwiden import vcs_clients
from openwiden.enums import OwnerType, VersionControlService, VisibilityLevel

DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def compare_dt_strings(original: str, compare: str) -> bool:
    original_dt = timezone.datetime.strptime(original, DATE_TIME_FORMAT)
    compare_dt = timezone.datetime.strptime(compare, DATE_TIME_FORMAT)
    return original_dt == compare_dt


@pytest.mark.django_db
@pytest.mark.functional
@mock.patch("requests.sessions.Session.request")
@pytest.mark.parametrize(
    "private_email", [pytest.param(False, id="public email"), pytest.param(True, id="private email"),]
)
def test_github(mock_request, create_api_client, private_email: bool, settings):
    settings.DEBUG = True
    mock_responses = []

    # Create API client
    api_client = create_api_client()

    # Create mock token fetch response
    mock_fetch_token_response = mock.MagicMock(
        json=mock.MagicMock(
            return_value={
                "access_token": "e72e16c7e42f292c6912e7710c838347ae178b4a",
                "scope": "repo,gist",
                "token_type": "bearer",
            }
        )
    )
    mock_responses.append(mock_fetch_token_response)

    # Create mock profile response
    mock_profile_json = {
        "login": "stefanitsky",
        "id": 22547214,
        "node_id": "MDQ6VXNlcjIyNTQ3MjE0",
        "avatar_url": "https://avatars3.githubusercontent.com/u/22547214?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/stefanitsky",
        "html_url": "https://github.com/stefanitsky",
        "followers_url": "https://api.github.com/users/stefanitsky/followers",
        "following_url": "https://api.github.com/users/stefanitsky/following{/other_user}",
        "gists_url": "https://api.github.com/users/stefanitsky/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/stefanitsky/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/stefanitsky/subscriptions",
        "organizations_url": "https://api.github.com/users/stefanitsky/orgs",
        "repos_url": "https://api.github.com/users/stefanitsky/repos",
        "events_url": "https://api.github.com/users/stefanitsky/events{/privacy}",
        "received_events_url": "https://api.github.com/users/stefanitsky/received_events",
        "type": "User",
        "site_admin": False,
        "name": "Alexandr Stefanitsky-Mozdor",
        "company": None,
        "blog": "",
        "location": "Russian Federation",
        "email": None if private_email else "stefanitsky.mozdor@gmail.com",
        "hireable": None,
        "bio": None,
        "twitter_username": None,
        "public_repos": 11,
        "public_gists": 1,
        "followers": 0,
        "following": 0,
        "created_at": "2016-09-30T15:43:07Z",
        "updated_at": "2020-07-24T14:57:55Z",
    }
    mock_profile_response = mock.MagicMock(json=mock.MagicMock(return_value=mock_profile_json))
    mock_responses.append(mock_profile_response)

    # Create mock email response
    if private_email:
        mock_emails_json = [
            {"email": "stefanitsky.mozdor@gmail.com", "verified": True, "primary": True, "visibility": "public"}
        ]
        mock_emails_response = mock.MagicMock(json=mock.MagicMock(return_value=mock_emails_json))
        mock_responses.append(mock_emails_response)

    # Create mock avatar response
    mock_avatar_response = mock.MagicMock(content=b"\0f")
    mock_responses.append(mock_avatar_response)

    # Create mock user repositories response
    mock_user_repositories_json = [  # noqa: E501
        {
            "id": 242516030,
            "node_id": "MDEwOlJlcG9zaXRvcnkyNDI1MTYwMzA=",
            "name": "openwiden-frontend",
            "full_name": "OpenWiden/openwiden-frontend",
            "private": False,
            "owner": {
                "login": "OpenWiden",
                "id": 59751674,
                "node_id": "MDEyOk9yZ2FuaXphdGlvbjU5NzUxNjc0",
                "avatar_url": "https://avatars3.githubusercontent.com/u/59751674?v=4",
                "gravatar_id": "",
                "url": "https://api.github.com/users/OpenWiden",
                "html_url": "https://github.com/OpenWiden",
                "followers_url": "https://api.github.com/users/OpenWiden/followers",
                "following_url": "https://api.github.com/users/OpenWiden/following{/other_user}",
                "gists_url": "https://api.github.com/users/OpenWiden/gists{/gist_id}",
                "starred_url": "https://api.github.com/users/OpenWiden/starred{/owner}{/repo}",
                "subscriptions_url": "https://api.github.com/users/OpenWiden/subscriptions",
                "organizations_url": "https://api.github.com/users/OpenWiden/orgs",
                "repos_url": "https://api.github.com/users/OpenWiden/repos",
                "events_url": "https://api.github.com/users/OpenWiden/events{/privacy}",
                "received_events_url": "https://api.github.com/users/OpenWiden/received_events",
                "type": "Organization",
                "site_admin": False,
            },
            "html_url": "https://github.com/OpenWiden/openwiden-frontend",
            "description": "OpenWiden - open source aggregator platform with a list of open source projects that helps developers find a great project and contribute to it.",  # noqa: E501
            "fork": False,
            "url": "https://api.github.com/repos/OpenWiden/openwiden-frontend",
            "forks_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/forks",
            "keys_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/keys{/key_id}",
            "collaborators_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/collaborators{/collaborator}",  # noqa: E501
            "teams_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/teams",
            "hooks_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/hooks",
            "issue_events_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/issues/events{/number}",
            "events_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/events",
            "assignees_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/assignees{/user}",
            "branches_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/branches{/branch}",
            "tags_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/tags",
            "blobs_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/git/blobs{/sha}",
            "git_tags_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/git/tags{/sha}",
            "git_refs_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/git/refs{/sha}",
            "trees_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/git/trees{/sha}",
            "statuses_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/statuses/{sha}",
            "languages_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/languages",
            "stargazers_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/stargazers",
            "contributors_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/contributors",
            "subscribers_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/subscribers",
            "subscription_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/subscription",
            "commits_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/commits{/sha}",
            "git_commits_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/git/commits{/sha}",
            "comments_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/comments{/number}",
            "issue_comment_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/issues/comments{/number}",
            "contents_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/contents/{+path}",
            "compare_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/compare/{base}...{head}",
            "merges_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/merges",
            "archive_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/{archive_format}{/ref}",
            "downloads_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/downloads",
            "issues_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/issues{/number}",
            "pulls_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/pulls{/number}",
            "milestones_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/milestones{/number}",
            "notifications_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/notifications{?since,all,participating}",  # noqa: E501
            "labels_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/labels{/name}",
            "releases_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/releases{/id}",
            "deployments_url": "https://api.github.com/repos/OpenWiden/openwiden-frontend/deployments",
            "created_at": "2020-02-23T12:50:01Z",
            "updated_at": "2020-06-26T15:13:53Z",
            "pushed_at": "2020-06-26T15:13:55Z",
            "git_url": "git://github.com/OpenWiden/openwiden-frontend.git",
            "ssh_url": "git@github.com:OpenWiden/openwiden-frontend.git",
            "clone_url": "https://github.com/OpenWiden/openwiden-frontend.git",
            "svn_url": "https://github.com/OpenWiden/openwiden-frontend",
            "homepage": "https://openwiden.com/",
            "size": 854,
            "stargazers_count": 0,
            "watchers_count": 0,
            "language": "Vue",
            "has_issues": True,
            "has_projects": True,
            "has_downloads": True,
            "has_wiki": True,
            "has_pages": False,
            "forks_count": 0,
            "mirror_url": None,
            "archived": False,
            "disabled": False,
            "open_issues_count": 6,
            "license": None,
            "forks": 0,
            "open_issues": 6,
            "watchers": 0,
            "default_branch": "develop",
            "permissions": {"admin": True, "push": True, "pull": True},
        },
        {
            "id": 250661059,
            "node_id": "MDEwOlJlcG9zaXRvcnkyNTA2NjEwNTk=",
            "name": "yandex_market_language",
            "full_name": "stefanitsky/yandex_market_language",
            "private": False,
            "owner": {
                "login": "stefanitsky",
                "id": 22547214,
                "node_id": "MDQ6VXNlcjIyNTQ3MjE0",
                "avatar_url": "https://avatars3.githubusercontent.com/u/22547214?v=4",
                "gravatar_id": "",
                "url": "https://api.github.com/users/stefanitsky",
                "html_url": "https://github.com/stefanitsky",
                "followers_url": "https://api.github.com/users/stefanitsky/followers",
                "following_url": "https://api.github.com/users/stefanitsky/following{/other_user}",
                "gists_url": "https://api.github.com/users/stefanitsky/gists{/gist_id}",
                "starred_url": "https://api.github.com/users/stefanitsky/starred{/owner}{/repo}",
                "subscriptions_url": "https://api.github.com/users/stefanitsky/subscriptions",
                "organizations_url": "https://api.github.com/users/stefanitsky/orgs",
                "repos_url": "https://api.github.com/users/stefanitsky/repos",
                "events_url": "https://api.github.com/users/stefanitsky/events{/privacy}",
                "received_events_url": "https://api.github.com/users/stefanitsky/received_events",
                "type": "User",
                "site_admin": False,
            },
            "html_url": "https://github.com/stefanitsky/yandex_market_language",
            "description": "Yandex Market Language for Python provides user-friendly interface for parsing or creating XML files.",  # noqa: E501
            "fork": False,
            "url": "https://api.github.com/repos/stefanitsky/yandex_market_language",
            "forks_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/forks",
            "keys_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/keys{/key_id}",
            "collaborators_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/collaborators{/collaborator}",  # noqa: E501
            "teams_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/teams",
            "hooks_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/hooks",
            "issue_events_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/issues/events{/number}",  # noqa: E501
            "events_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/events",
            "assignees_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/assignees{/user}",
            "branches_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/branches{/branch}",
            "tags_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/tags",
            "blobs_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/git/blobs{/sha}",
            "git_tags_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/git/tags{/sha}",
            "git_refs_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/git/refs{/sha}",
            "trees_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/git/trees{/sha}",
            "statuses_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/statuses/{sha}",
            "languages_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/languages",
            "stargazers_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/stargazers",
            "contributors_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/contributors",
            "subscribers_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/subscribers",
            "subscription_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/subscription",
            "commits_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/commits{/sha}",
            "git_commits_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/git/commits{/sha}",
            "comments_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/comments{/number}",
            "issue_comment_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/issues/comments{/number}",  # noqa: E501
            "contents_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/contents/{+path}",
            "compare_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/compare/{base}...{head}",
            "merges_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/merges",
            "archive_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/{archive_format}{/ref}",
            "downloads_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/downloads",
            "issues_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/issues{/number}",
            "pulls_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/pulls{/number}",
            "milestones_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/milestones{/number}",
            "notifications_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/notifications{?since,all,participating}",  # noqa: E501
            "labels_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/labels{/name}",
            "releases_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/releases{/id}",
            "deployments_url": "https://api.github.com/repos/stefanitsky/yandex_market_language/deployments",
            "created_at": "2020-03-27T22:21:23Z",
            "updated_at": "2020-07-26T10:15:15Z",
            "pushed_at": "2020-07-26T10:15:13Z",
            "git_url": "git://github.com/stefanitsky/yandex_market_language.git",
            "ssh_url": "git@github.com:stefanitsky/yandex_market_language.git",
            "clone_url": "https://github.com/stefanitsky/yandex_market_language.git",
            "svn_url": "https://github.com/stefanitsky/yandex_market_language",
            "homepage": None,
            "size": 192,
            "stargazers_count": 3,
            "watchers_count": 3,
            "language": "Python",
            "has_issues": True,
            "has_projects": True,
            "has_downloads": True,
            "has_wiki": True,
            "has_pages": False,
            "forks_count": 2,
            "mirror_url": None,
            "archived": False,
            "disabled": False,
            "open_issues_count": 2,
            "license": {
                "key": "other",
                "name": "Other",
                "spdx_id": "NOASSERTION",
                "url": None,
                "node_id": "MDc6TGljZW5zZTA=",
            },
            "forks": 2,
            "open_issues": 2,
            "watchers": 3,
            "default_branch": "master",
            "permissions": {"admin": True, "push": True, "pull": True},
        },
    ]
    mock_user_repositories_response = mock.MagicMock(
        json=mock.MagicMock(return_value=deepcopy(mock_user_repositories_json)), status_code=200,
    )
    mock_responses.append(mock_user_repositories_response)

    # Mock side effect for authlib requests
    mock_request.side_effect = mock_responses

    # Make request to auth complete view
    auth_complete_response = api_client.get(reverse("v1:auth-complete", kwargs={"vcs": VersionControlService.GITHUB}))

    # Test auth complete view response
    assert auth_complete_response.status_code == 200
    assert list(auth_complete_response.data.keys()) == ["access", "refresh"]

    # Recreate API client with access token
    api_client = create_api_client(access_token=auth_complete_response.data["access"])

    # Make request to get user repositories
    user_repositories_response = api_client.get(reverse("api-v1:user-repositories-list"))

    # Test synced user repositories data
    assert user_repositories_response.data["count"] == len(mock_user_repositories_json)
    for user_repository_data, raw_repository_data in zip(
        user_repositories_response.data["results"], mock_user_repositories_json,
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
