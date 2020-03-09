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
