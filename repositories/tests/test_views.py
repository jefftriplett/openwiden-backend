from django.core import management
from rest_framework import status
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase

from repositories.tests.factories import RepositoryFactory


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

    def test_add_view(self):
        management.call_command("loaddata", "version_control_services.json", verbosity=0)
        git_urls = (
            # "https://gitlab.com/inkscape/inkscape",
            # "https://gitlab.com/gnachman/iterm2",
            # "https://gitlab.com/pgjones/quart",
            "https://github.com/golang/go",
            "https://github.com/getsentry/sentry",
            "https://github.com/sveltejs/svelte",
        )
        for url in git_urls:
            response = self.client.post(reverse_lazy("repository-add"), data={"url": url})
            self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
            self.assertEqual(response.data["url"], url)
        self.assertEqual(RepositoryFactory._meta.model.objects.count(), len(git_urls))
