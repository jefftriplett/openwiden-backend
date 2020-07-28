from unittest import mock

import pytest
from django.urls import reverse
from rest_framework import status

from openwiden.enums import VersionControlService
from openwiden.webhooks import models as webhook_models


@pytest.mark.functional
@pytest.mark.django_db
@mock.patch("requests.sessions.Session.request")
@pytest.mark.parametrize("vcs", VersionControlService.values)
def test_run(
    mock_request,
    user,
    create_vcs_account,
    create_api_client,
    create_repository,
    create_repo_webhook,
    vcs,
    create_mock_response,
):
    vcs_account = create_vcs_account(vcs=vcs)
    api_client = create_api_client(user=vcs_account.user)
    repository = create_repository(vcs=vcs, is_added=True, owner=vcs_account, organization=None)
    create_repo_webhook(repository=repository)

    # Mock request
    mock_request.return_value = create_mock_response(status_code=204)

    # Make remove repository request
    url = reverse("api-v1:user-repositories-remove", kwargs={"id": str(repository.id)})
    response = api_client.delete(url)
    repository.refresh_from_db()

    # Test response
    assert response.status_code == status.HTTP_204_NO_CONTENT, print(response.data)

    # Test repository
    assert repository.is_added is False
    assert not webhook_models.RepositoryWebhook.objects.filter(repository=repository).exists()
