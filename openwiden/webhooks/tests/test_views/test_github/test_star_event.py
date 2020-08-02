from unittest import mock

import pytest
from django.urls import reverse
from rest_framework import status

from openwiden.enums import VersionControlService

STAR = {
  "action": "created",
  "starred_at": "2020-08-02T14:45:19Z",
  "repository": {
    "id": 284474343,
    "node_id": "MDEwOlJlcG9zaXRvcnkyODQ0NzQzNDM=",
    "name": "test-repository-for-webhook",
    "full_name": "stefanitsky/test-repository-for-webhook",
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
      "site_admin": False
    },
    "html_url": "https://github.com/stefanitsky/test-repository-for-webhook",
    "description": "Test repository for webhook tests.",
    "fork": False,
    "url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook",
    "forks_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/forks",
    "keys_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/keys{/key_id}",
    "collaborators_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/collaborators{/collaborator}",
    "teams_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/teams",
    "hooks_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/hooks",
    "issue_events_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/issues/events{/number}",
    "events_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/events",
    "assignees_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/assignees{/user}",
    "branches_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/branches{/branch}",
    "tags_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/tags",
    "blobs_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/git/blobs{/sha}",
    "git_tags_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/git/tags{/sha}",
    "git_refs_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/git/refs{/sha}",
    "trees_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/git/trees{/sha}",
    "statuses_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/statuses/{sha}",
    "languages_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/languages",
    "stargazers_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/stargazers",
    "contributors_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/contributors",
    "subscribers_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/subscribers",
    "subscription_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/subscription",
    "commits_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/commits{/sha}",
    "git_commits_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/git/commits{/sha}",
    "comments_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/comments{/number}",
    "issue_comment_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/issues/comments{/number}",
    "contents_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/contents/{+path}",
    "compare_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/compare/{base}...{head}",
    "merges_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/merges",
    "archive_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/{archive_format}{/ref}",
    "downloads_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/downloads",
    "issues_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/issues{/number}",
    "pulls_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/pulls{/number}",
    "milestones_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/milestones{/number}",
    "notifications_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/notifications{?since,all,participating}",
    "labels_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/labels{/name}",
    "releases_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/releases{/id}",
    "deployments_url": "https://api.github.com/repos/stefanitsky/test-repository-for-webhook/deployments",
    "created_at": "2020-08-02T14:09:46Z",
    "updated_at": "2020-08-02T14:45:19Z",
    "pushed_at": "2020-08-02T14:09:48Z",
    "git_url": "git://github.com/stefanitsky/test-repository-for-webhook.git",
    "ssh_url": "git@github.com:stefanitsky/test-repository-for-webhook.git",
    "clone_url": "https://github.com/stefanitsky/test-repository-for-webhook.git",
    "svn_url": "https://github.com/stefanitsky/test-repository-for-webhook",
    "homepage": "",
    "size": 0,
    "stargazers_count": 1,
    "watchers_count": 1,
    "language": None,
    "has_issues": True,
    "has_projects": True,
    "has_downloads": True,
    "has_wiki": True,
    "has_pages": False,
    "forks_count": 0,
    "mirror_url": None,
    "archived": False,
    "disabled": False,
    "open_issues_count": 0,
    "license": None,
    "forks": 0,
    "open_issues": 0,
    "watchers": 1,
    "default_branch": "master"
  },
  "sender": {
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
    "site_admin": False
  }
}


@pytest.mark.functional
@pytest.mark.django_db
@mock.patch("github_webhooks.utils.compare_signatures")
def test_run(
    mock_compare_signatures,
    create_repository,
    create_repo_webhook,
    create_api_client,
):
    mock_compare_signatures.return_value = True
    api_client = create_api_client()
    repository = create_repository(
        vcs=VersionControlService.GITHUB,
        remote_id=STAR["repository"]["id"],
    )
    repository_webhook = create_repo_webhook(repository=repository, secret=12345)

    # Make webhook event request
    url = reverse("v1:webhooks:github", kwargs={"id": str(repository_webhook.id)})
    response = api_client.post(
        url,
        data=STAR,
        format="json",
        # Headers
        **{
            "HTTP_X_GITHUB_EVENT": "star",
            "HTTP_X_HUB_SIGNATURE": "sha1=12345",
        },
    )

    # Test
    assert response.status_code == status.HTTP_200_OK, print(response.json())
    repository.refresh_from_db()
    assert repository.stars_count == STAR["repository"]["stargazers_count"]
