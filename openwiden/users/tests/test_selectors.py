from unittest import mock

import pytest

from openwiden import exceptions
from openwiden.users import models, selectors, messages

pytestmark = pytest.mark.django_db


@mock.patch.object(models.VCSAccount.objects, "get")
def test_find(patched_objects_get, mock_vcs_account, mock_user):
    patched_objects_get.return_value = mock_vcs_account
    vcs_account = selectors.find_vcs_account(mock_user, "test")

    assert vcs_account == mock_vcs_account


@mock.patch.object(models.VCSAccount.objects, "get")
def test_find_raises_service_exception(patched_objects_get, mock_user):
    def raise_does_not_exist(**kwargs):
        raise selectors.models.VCSAccount.DoesNotExist

    patched_objects_get.side_effect = raise_does_not_exist

    with pytest.raises(exceptions.ServiceException) as e:
        selectors.find_vcs_account(mock_user, "test")

        assert e.value == messages.VCS_ACCOUNT_DOES_NOT_EXIST.format(vcs="test")
