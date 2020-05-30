import pytest

from openwiden.exceptions import ServiceException
from openwiden.services import utils, constants
from openwiden.services.github import GitHubService
from openwiden.services.gitlab import GitlabService
from openwiden.enums import VersionControlService

pytestmark = pytest.mark.django_db


test_get_service_data = [
    (VersionControlService.GITHUB.value, GitHubService),
    (VersionControlService.GITLAB.value, GitlabService),
]


@pytest.mark.parametrize("vcs,expected_cls", test_get_service_data)
def test_get_service(vcs, expected_cls):
    assert isinstance(utils.get_service(vcs=vcs), expected_cls)


def test_get_service_raises_exception():
    vcs = "error"

    with pytest.raises(ServiceException) as e:
        utils.get_service(vcs=vcs)

    assert e.value.description == constants.Messages.VCS_IS_NOT_IMPLEMENTED.format(vcs=vcs)


def test_get_service_args_assert(vcs_account, random_vcs):
    with pytest.raises(AssertionError) as e:
        utils.get_service()

    assert e.value.args[0] == "vcs_account or vcs name should be specified."

    with pytest.raises(AssertionError) as e:
        utils.get_service(vcs_account=vcs_account, vcs=random_vcs)

    assert e.value.args[0] == "only vcs_account or vcs should be specified"
