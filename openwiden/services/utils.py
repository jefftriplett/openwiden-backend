from openwiden.users import models
from openwiden import enums, exceptions
from .abstract import RemoteService
from .github import GitHubService
from .gitlab import GitlabService


def get_service(*, vcs_account: models.VCSAccount = None, vcs: str = None) -> RemoteService:
    """
    Returns remote API service class instance depends on specified vcs_account.
    """
    assert vcs_account or vcs, "vcs_account or vcs name should be specified."

    vcs = vcs or vcs_account.vcs
    if vcs == enums.VersionControlService.GITHUB:
        return GitHubService(vcs_account=vcs_account, vcs=vcs)
    elif vcs == enums.VersionControlService.GITLAB:
        return GitlabService(vcs_account=vcs_account, vcs=vcs)
    else:
        raise exceptions.ServiceException(f"{vcs} is not implemented!")
