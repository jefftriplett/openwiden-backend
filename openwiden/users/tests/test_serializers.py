import pytest

from openwiden.users import serializers

pytestmark = pytest.mark.django_db


def test_vcs_account_serializer(vcs_account):
    assert serializers.VCSAccountSerializer(vcs_account).data == {"vcs": vcs_account.vcs, "login": vcs_account.login}
