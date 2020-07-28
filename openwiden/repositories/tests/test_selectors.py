import pytest

from openwiden.repositories import selectors, models

pytestmark = pytest.mark.django_db


def test_get_user_repositories(create_repository, user, org, create_member, create_vcs_account):
    user_repos = [
        create_repository(owner__user=user, organization=None),
        create_repository(owner=None, organization=org),
    ]
    create_repository(owner=None, organization=None)
    create_member(organization=org, vcs_account=create_vcs_account(user=user))

    qs = selectors.get_user_repositories(user=user)

    assert qs.count() == len(user_repos)
    assert models.Repository.objects.count() == len(user_repos) + 1
