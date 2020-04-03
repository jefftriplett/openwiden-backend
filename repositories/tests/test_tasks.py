from datetime import datetime

import mock
from faker import Faker

from django.test import TestCase

from repositories import tasks
from repositories.tests.factories import RepositoryFactory
from users.tests.factories import UserFactory

fake = Faker()

DATETIME_FORMAT = "%m/%d/%Y %I:%M %p"


def random_datetime():
    return datetime.strptime(fake.date(DATETIME_FORMAT), DATETIME_FORMAT)


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
        self.created_at = random_datetime()
        self.updated_at = random_datetime()
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
        self.created_at = random_datetime()
        self.updated_at = random_datetime()
        self.open_issues_count = issues_count + pull_requests_count
        self.private = private
        self._issues_count = issues_count
        self._pull_requests_count = pull_requests_count

    def get_issues(self):
        return [Issue() for _ in range(self._issues_count)] + [PullRequest() for _ in range(self._pull_requests_count)]


class AddGitHubRepositoryTask(TestCase):
    def test_already_exists(self):
        pass

    def test_is_private(self):
        pass

    def test_excludes_pull_requests(self):
        pass

    def test_sets_programming_languages(self):
        pass


@mock.patch("repositories.tasks.send_mail")
class AddGitHubRepositoryTaskSendEmail(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()

    def test_exists(self, send_mail_patched):
        tasks.add_github_repository_send_email("exists", self.user)
        self.assertEqual(send_mail_patched.call_count, 1)

    def test_private(self, send_mail_patched):
        tasks.add_github_repository_send_email("private", self.user)
        self.assertEqual(send_mail_patched.call_count, 1)

    def test_added(self, send_mail_patched):
        repository = RepositoryFactory.create()
        tasks.add_github_repository_send_email("added", self.user, repository)
        self.assertEqual(send_mail_patched.call_count, 1)

    def test_raises_error(self, send_mail_patched):
        with self.assertRaises(ValueError) as e:
            tasks.add_github_repository_send_email("err", self.user)
            self.assertEqual(str(e), "Unknown result of type err")
        self.assertEqual(send_mail_patched.call_count, 0)
