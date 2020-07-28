import pytest


pytestmark = pytest.mark.django_db


class TestOrganizationModel:
    def test_str(self, org):
        assert str(org) == org.name


class TestMemberModel:
    def test_str(self, member):
        assert str(member) == member.vcs_account.login
