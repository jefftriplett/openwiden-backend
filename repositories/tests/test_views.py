from datetime import datetime

import mock
from django.core import management
from faker import Faker
from rest_framework import status
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase

from repositories.exceptions import RepositoryURLParse, VersionControlServiceNotFound
from repositories.tests.factories import RepositoryFactory

fake = Faker()
datetime_format = "%m/%d/%Y %I:%M %p"


class Repository:
    def __init__(self, url: str, private: bool = False):
        self.id = fake.pyint()
        self.name = fake.name()
        self.description = fake.text()
        self.html_url = url
        self.forks_count = fake.pyint()
        self.stargazers_count = fake.pyint()
        self.created_at = datetime.strptime(fake.date(datetime_format), datetime_format)
        self.updated_at = datetime.strptime(fake.date(datetime_format), datetime_format)
        self.open_issues_count = fake.pyint()
        self.private = private


class RepositoryViewSetTestCase(APITestCase):
    def test_list_view(self):
        repositories = RepositoryFactory.create_batch(5)
        response = self.client.get(reverse_lazy("repository-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), len(repositories))

    def test_retrieve_view(self):
        repository = RepositoryFactory.create()
        response = self.client.get(reverse_lazy("repository-detail", kwargs={"id": str(repository.id)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(repository.id))

    @mock.patch("repositories.views.github.get_repo")
    def test_add_view(self, patched_get_repo):
        management.call_command("loaddata", "version_control_services.json", verbosity=0)
        git_urls = (
            # "https://gitlab.com/pgjones/quart",
            "https://github.com/golang/go",
        )
        for url in git_urls:
            patched_get_repo.return_value = Repository(url=url)
            response = self.client.post(reverse_lazy("repository-add"), data={"url": url})
            self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
            self.assertEqual(response.data["url"], url)
        self.assertEqual(RepositoryFactory._meta.model.objects.count(), len(git_urls))

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
