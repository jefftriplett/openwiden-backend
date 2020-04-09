from datetime import datetime

import mock
from faker import Faker

from django.test import TestCase

from openwiden.repositories import tasks
from openwiden.repositories import models
from openwiden.repositories.tests import factories
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


@mock.patch("openwiden.repositories.tasks.send_mail")
class AddGitHubRepositoryTaskSendEmail(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()

    def test_exists(self, send_mail_patched):
        tasks.add_repository_send_email("exists", self.user)
        self.assertEqual(send_mail_patched.call_count, 1)

    def test_rate_limit_exceeded(self, send_mail_patched):
        tasks.add_repository_send_email("rate_limit_exceeded", self.user)
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


class AddRepository(TestCase):
    @mock.patch("openwiden.repositories.tasks.requests.get")
    @mock.patch("openwiden.repositories.tasks.async_task")
    @mock.patch.object(tasks.gitlab.projects, "get")
    @mock.patch.object(tasks.github, "get_repo")
    def test_add_repository(self, patched_github, patched_gitlab, patched_async_task, patched_requests_get):
        user = UserFactory()
        service = factories.VersionControlService(host="github.com")
        github_fake_repo = Repository()
        gitlab_fake_repo = Repository(issues_count=0, pull_requests_count=0)
        patched_github.return_value = github_fake_repo
        patched_gitlab.return_value = gitlab_fake_repo
        result = tasks.add_repository(user, service, "test_owner", "test_repo")
        repository = models.Repository.objects.get(version_control_service=service, remote_id=github_fake_repo.id)
        self.assertEqual(result, f"{repository.name} was added (id: {repository.id})")
        patched_github.assert_called_once()
        patched_async_task.assert_called_with(tasks.add_issues, github_fake_repo, repository)

        # Test already exists
        result = tasks.add_repository(user, service, "test_owner", "test_repo")
        self.assertEqual(result, f"{repository.name} already exists (id: {repository.id})")
        patched_async_task.assert_called_with(tasks.add_repository_send_email, "exists", user, repository)

        # Test gitlab repository
        service = factories.VersionControlService(host="gitlab.com")
        result = tasks.add_repository(user, service, "test_owner", "test_repo")
        repository = models.Repository.objects.get(version_control_service=service, remote_id=gitlab_fake_repo.id)
        self.assertEqual(result, f"{repository.name} was added (id: {repository.id})")
        patched_gitlab.assert_called_once()

    def test_add_github_repository_service_not_implemented(self):
        user = UserFactory()
        service = factories.VersionControlService(host="not-implemented.com")
        with self.assertRaisesMessage(NotImplementedError, f"{service} is not implemented!"):
            tasks.add_repository(user, service, "test_owner", "test_user")

    @mock.patch("openwiden.repositories.tasks.async_task")
    @mock.patch.object(tasks.github, "get_repo")
    def test_rate_limit_exceeded(self, patched_get_repo, patched_async_task):
        owner, repo = "test_owner", "test_repo"
        user = UserFactory()
        service = factories.VersionControlService(host="github.com")
        patched_get_repo.side_effect = tasks.RateLimitExceededException("err", "now")
        result = tasks.add_repository(user, service, owner, repo)
        patched_async_task.assert_called_once_with(tasks.add_repository_send_email, "rate_limit_exceeded", user)
        self.assertEqual(result, f"Rate limit exceeded for {owner}/{repo} add request.")


class AddIssues(TestCase):
    def test_add_issues_github(self):
        fake_repo = Repository()
        factory_repo = factories.Repository(version_control_service__host="github.com")
        result = tasks.add_issues(fake_repo, factory_repo)
        self.assertEqual(
            result, f"Issues created successfully for repository {factory_repo}: {len(fake_repo.issues.list())}"
        )

    def test_add_issues_gitlab(self):
        fake_repo = Repository()
        factory_repo = factories.Repository(version_control_service__host="gitlab.com")
        result = tasks.add_issues(fake_repo, factory_repo)
        self.assertEqual(
            result, f"Issues created successfully for repository {factory_repo}: {len(fake_repo.issues.list())}"
        )

    def test_add_issues_not_implemented(self):
        fake_repo = Repository()
        factory_repo = factories.Repository(version_control_service__host="not-implemented.com")
        with self.assertRaisesMessage(
            NotImplementedError, f"{factory_repo.version_control_service} is not implemented for issues download!"
        ):
            tasks.add_issues(fake_repo, factory_repo)
