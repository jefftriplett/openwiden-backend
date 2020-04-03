import mock
from django.core import management
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from repositories.exceptions import RepositoryURLParse, VersionControlServiceNotFound
from repositories.tests.factories import RepositoryFactory, IssueFactory
from users.tests.factories import UserFactory


class RepositoryViewSetTestCase(APITestCase):
    def add_auth_header(self):
        user = UserFactory.create()
        access_token = str(RefreshToken.for_user(user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {access_token}")

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

    def test_add_view_not_authenticated(self):
        response = self.client.post(reverse_lazy("repository-add"), data={"url": "test"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @mock.patch("repositories.views.async_task")
    def test_add_view_wih_github(self, patched_task):
        management.call_command("loaddata", "version_control_services.json", verbosity=0)
        url = "https://github.com/golang/go"
        self.add_auth_header()
        response = self.client.post(reverse_lazy("repository-add"), data={"url": url})
        self.assertEqual(patched_task.call_count, 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
        self.assertEqual(
            response.data, {"detail": _("Thank you! Repository will be added soon, you will be notified by e-mail.")}
        )

    def test_add_view_with_gitlab(self):
        management.call_command("loaddata", "version_control_services.json", verbosity=0)
        url = "https://gitlab.com/pgjones/quart"
        self.add_auth_header()
        response = self.client.post(reverse_lazy("repository-add"), data={"url": url})
        self.assertEqual(response.status_code, status.HTTP_501_NOT_IMPLEMENTED)
        self.assertEqual(response.data, {"detail": _(f"Not implemented yet.")})

    @mock.patch("repositories.views.parse_repo_url")
    def test_add_view_raises_repo_url_parse_error(self, patched_parse_repo_url):
        patched_parse_repo_url.return_value = None
        url = "https://github.com/golang/go"
        self.add_auth_header()
        response = self.client.post(reverse_lazy("repository-add"), data={"url": url})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"detail": RepositoryURLParse(url).detail})

    def test_add_view_raises_vcs_not_found(self):
        url = "https://example.com/golang/go"
        self.add_auth_header()
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
