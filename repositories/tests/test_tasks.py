from datetime import datetime

import mock
from faker import Faker

from django.test import TestCase

from repositories import tasks
from repositories import models
from repositories.tests import factories
from users.tests.factories import UserFactory

fake = Faker()

DATETIME_FORMAT = "%m/%d/%Y %I:%M %p"


def random_datetime():
    return datetime.strptime(fake.date(DATETIME_FORMAT), DATETIME_FORMAT)


class Label:
    def __init__(self):
        self.name = fake.word()


class Issue:
    def __init__(self, gitlab: bool = False):
        self.id = fake.pyint()
        self.title = fake.word()
        self.body = fake.text()
        self.state = "open"
        self.labels = [Label().name if gitlab else Label() for _ in range(3)]
        self.html_url = fake.url()
        self.created_at = random_datetime()
        self.updated_at = random_datetime()
        self.closed_at = None
        self.pull_request = None

    @property
    def description(self):
        return self.body

    def web_url(self):
        return self.html_url


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
    def __init__(
        self,
        id: int = fake.pyint(),
        url: str = fake.url(),
        private: bool = False,
        issues_count: int = 5,
        pull_requests_count: int = 3,
    ):
        self.id = id
        self.name = fake.name()
        self.description = fake.text()
        self.html_url = url
        self.forks_count = fake.pyint()
        self.stargazers_count = fake.pyint()
        self.created_at = random_datetime()
        self.updated_at = random_datetime()
        self.open_issues_count = issues_count + pull_requests_count
        self.private = private
        self._issues_count = issues_count
        self._pull_requests_count = pull_requests_count

    @property
    def web_url(self):
        return self.html_url

    @property
    def star_count(self):
        return self.stargazers_count

    @property
    def last_activity_at(self):
        return self.updated_at

    def get_issues(self, state):
        return [Issue() for _ in range(self._issues_count)] + [PullRequest() for _ in range(self._pull_requests_count)]

    @property
    def issues(self):
        """
        Gitlab issues mock.
        """

        class MockList:
            def __init__(self, issues_count: int = 3):
                self.issues_count = issues_count

            def list(self, *args, **kwargs):
                return [Issue(gitlab=True) for _ in range(self.issues_count)]

        return MockList(issues_count=self._issues_count)

    @staticmethod
    def get_languages():
        return {"Shell": "94", "Python": "79298", "Makefile": "1569", "Dockerfile": "334"}

    def languages(self):
        """
        Gitlab mock.
        """
        return self.get_languages()


@mock.patch("repositories.tasks.github.get_repo", return_value=Repository())
@mock.patch("repositories.tasks.async_task")
class AddGitHubRepositoryTask(TestCase):
    @classmethod
    def setUpTestData(cls):
        parsed_url = mock.MagicMock()
        parsed_url.owner = "owner_test"
        parsed_url.repo = "repo_test"
        cls.user = UserFactory.create()
        cls.parsed_url = parsed_url
        cls.service = factories.VersionControlService.create()

    def test_already_exists(self, patched_async_task, patched_get_repo):
        fake_repo = Repository()
        factories.Repository.create(version_control_service=self.service, remote_id=str(fake_repo.id))
        patched_get_repo.return_value = fake_repo
        tasks.add_github_repository(self.user, self.parsed_url, self.service)
        self.assertEqual(patched_get_repo.call_count, 1)
        patched_async_task.assert_called_once_with(tasks.add_repository_send_email, "exists", self.user)

    def test_is_private(self, patched_async_task, patched_get_repo):
        patched_get_repo.return_value = Repository(private=True)
        tasks.add_github_repository(self.user, self.parsed_url, self.service)
        self.assertEqual(patched_get_repo.call_count, 1)
        patched_async_task.assert_called_once_with(tasks.add_repository_send_email, "private", self.user)

    def test_excludes_pull_requests_and_adds_repository_successfully(self, patched_async_task, patched_get_repo):
        issues_count = 5
        fake_repo = Repository(issues_count=issues_count, pull_requests_count=3)
        patched_get_repo.return_value = fake_repo
        tasks.add_github_repository(self.user, self.parsed_url, self.service)
        created_repository = models.Repository.objects.get(remote_id=str(fake_repo.id))
        self.assertEqual(patched_get_repo.call_count, 1)
        self.assertEqual(created_repository.issues.count(), issues_count)
        patched_async_task.assert_called_once_with(
            tasks.add_repository_send_email, "added", self.user, created_repository
        )


@mock.patch("repositories.tasks.send_mail")
class AddGitHubRepositoryTaskSendEmail(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()

    def test_exists(self, send_mail_patched):
        tasks.add_repository_send_email("exists", self.user)
        self.assertEqual(send_mail_patched.call_count, 1)

    def test_private(self, send_mail_patched):
        tasks.add_repository_send_email("private", self.user)
        self.assertEqual(send_mail_patched.call_count, 1)

    def test_added(self, send_mail_patched):
        repository = factories.Repository.create()
        tasks.add_repository_send_email("added", self.user, repository)
        self.assertEqual(send_mail_patched.call_count, 1)

    def test_raises_error(self, send_mail_patched):
        with self.assertRaises(ValueError) as e:
            tasks.add_repository_send_email("err", self.user)
            self.assertEqual(str(e), "Unknown result of type err")
        self.assertEqual(send_mail_patched.call_count, 0)


@mock.patch("repositories.tasks.requests.get")
@mock.patch("repositories.tasks.gitlab.projects.get", return_value=Repository())
@mock.patch("repositories.tasks.async_task")
class AddGitlabRepositoryTask(TestCase):
    @classmethod
    def setUpTestData(cls):
        parsed_url = mock.MagicMock()
        parsed_url.owner = "owner_test"
        parsed_url.repo = "repo_test"
        cls.user = UserFactory.create()
        cls.parsed_url = parsed_url
        cls.service = factories.VersionControlService.create()

    def test_add_gitlab_repository(self, patched_async_task, patched_projects_get, patched_requests_get):
        tasks.add_gitlab_repository(self.user, self.parsed_url, self.service)
        repository = models.Repository.objects.first()
        patched_async_task.assert_called_once_with(tasks.add_repository_send_email, "added", self.user, repository)

    def test_add_gitlab_repository_already_exists(self, patched_async_task, patched_projects_get, patched_requests_get):
        fake_repo = Repository()
        patched_projects_get.return_value = fake_repo
        factories.Repository.create(version_control_service=self.service, remote_id=str(fake_repo.id))
        tasks.add_gitlab_repository(self.user, self.parsed_url, self.service)
        patched_async_task.assert_called_once_with(tasks.add_repository_send_email, "exists", self.user)
