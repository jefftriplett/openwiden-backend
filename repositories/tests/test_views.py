from datetime import datetime

import mock
from django.core import management
from faker import Faker
from rest_framework import status
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase

from repositories.exceptions import RepositoryURLParse, VersionControlServiceNotFound
from repositories.tests.factories import RepositoryFactory, IssueFactory

fake = Faker()
datetime_format = "%m/%d/%Y %I:%M %p"


class Label:
    def __init__(self):
        self.name = fake.word()


class Issue:
    def __init__(self):
        self.id = fake.pyint()
        self.title = fake.word()
        self.body = fake.text()
        self.state = "open"
        self.labels = [Label() for _ in range(3)]
        self.html_url = fake.url()
        self.created_at = datetime.strptime(fake.date(datetime_format), datetime_format)
        self.updated_at = datetime.strptime(fake.date(datetime_format), datetime_format)
        self.closed_at = None
        self.pull_request = None


class PullRequest(Issue):
    def __init__(self):
        super().__init__()
        self.pull_request = {
            "url": "https://api.github.com/repos/octocat/Hello-World/pulls/1347",
            "html_url": "https://github.com/octocat/Hello-World/pull/1347",
            "diff_url": "https://github.com/octocat/Hello-World/pull/1347.diff",
            "patch_url": "https://github.com/octocat/Hello-World/pull/1347.patch",
        }


class Repository:
    def __init__(self, url: str, private: bool = False, issues_count: int = 5, pull_requests_count: int = 3):
        self.id = fake.pyint()
        self.name = fake.name()
        self.description = fake.text()
        self.html_url = url
        self.forks_count = fake.pyint()
        self.stargazers_count = fake.pyint()
        self.created_at = datetime.strptime(fake.date(datetime_format), datetime_format)
        self.updated_at = datetime.strptime(fake.date(datetime_format), datetime_format)
        self.open_issues_count = issues_count + pull_requests_count
        self.private = private
        self._issues_count = issues_count
        self._pull_requests_count = pull_requests_count

    def get_issues(self, *args, **kwargs):
        return [Issue() for _ in range(self._issues_count)] + [PullRequest() for _ in range(self._pull_requests_count)]


class RepositoryViewSetTestCase(APITestCase):
    def test_list_view(self):
        repositories = RepositoryFactory.create_batch(5)
        response = self.client.get(reverse_lazy("repository-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], len(repositories))

    def test_retrieve_view(self):
        repository = RepositoryFactory.create()
        response = self.client.get(reverse_lazy("repository-detail", kwargs={"id": str(repository.id)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(repository.id))

    @mock.patch("repositories.views.github.get_repo")
    def test_add_view_wih_github(self, patched_get_repo):
        management.call_command("loaddata", "version_control_services.json", verbosity=0)
        url = "https://github.com/golang/go"
        mock_repo = Repository(url=url)
        patched_get_repo.return_value = mock_repo
        response = self.client.post(reverse_lazy("repository-add"), data={"url": url})
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
        self.assertEqual(response.data["url"], url)
        self.assertEqual(response.data["open_issues_count"], mock_repo._issues_count)

    def test_add_view_with_gitlab(self):
        # "https://gitlab.com/pgjones/quart"
        self.skipTest("todo")

    @mock.patch("repositories.views.parse_repo_url")
    def test_add_view_raises_repo_url_parse_error(self, patched_parse_repo_url):
        patched_parse_repo_url.return_value = None
        url = "https://github.com/golang/go"
        response = self.client.post(reverse_lazy("repository-add"), data={"url": url})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"detail": RepositoryURLParse(url).detail})

    def test_add_view_raises_vcs_not_found(self):
        url = "https://example.com/golang/go"
        response = self.client.post(reverse_lazy("repository-add"), data={"url": url})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"detail": VersionControlServiceNotFound("example.com").detail})


class IssueViewSetTestCase(APITestCase):
    def test_list_action(self):
        repository = RepositoryFactory.create()
        issues = IssueFactory.create_batch(repository=repository, size=3)
        response = self.client.get(reverse_lazy("issue-list", kwargs={"repository_id": str(repository.id)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], len(issues))

    def test_retrieve_action(self):
        issue = IssueFactory.create()
        repository = issue.repository
        issue_id = str(issue.id)
        kwargs = {"repository_id": str(repository.id), "id": issue_id}
        response = self.client.get(reverse_lazy("issue-detail", kwargs=kwargs))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], issue_id)
