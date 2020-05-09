from openwiden.users import models
from openwiden import enums
from .abstract import RemoteService
from .github import GitHubService
from .gitlab import GitlabService


def get_service(vcs_account: models.VCSAccount) -> RemoteService:
    """
    Returns remote API service class instance depends on specified vcs_account.
    """
    if vcs_account.vcs == enums.VersionControlService.GITHUB:
        return GitHubService(vcs_account)
    elif vcs_account.vcs == enums.VersionControlService.GITLAB:
        return GitlabService(vcs_account)
    else:
        raise NotImplementedError(f"{vcs_account.vcs} is not implemented!")
