import pytest
from unittest import mock

from openwiden.organizations import services, models


class TestOrganizationService:
    @mock.patch.object(models.Organization.objects, "update_or_create")
    def test_sync(self, patched_update_or_create, mock_org):
        patched_update_or_create.return_value = mock_org, True

        assert services.Organization.sync("", 1, "") == (mock_org, True)
        assert patched_update_or_create.call_count == 1

    @pytest.mark.django_db
    def test_remove_member(self, org, create_member, vcs_account):
        create_member(organization=org, vcs_account=vcs_account)

        assert org.members.count() == 1

        services.Organization.remove_member(org, vcs_account)

        assert org.members.count() == 0


class TestMemberService:
    @mock.patch.object(models.Member.objects, "update_or_create")
    def test_sync(self, patched_update_or_create, mock_member, mock_org, mock_vcs_account):
        expected = (mock_member, False)
        patched_update_or_create.return_value = expected

        assert services.Member.sync(mock_org, mock_vcs_account, False) == expected
