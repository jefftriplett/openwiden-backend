from openwiden.users import models
from openwiden import enums
from .abstract import RemoteService
from .github import GitHubService
from .gitlab import GitlabService


def get_service(oauth_token: models.VCSAccount) -> RemoteService:
    """
    Returns remote API service class instance depends on specified vcs_account.
    """
    if oauth_token.provider == enums.VersionControlService.GITHUB:
        return GitHubService(oauth_token)
    elif oauth_token.provider == enums.VersionControlService.GITLAB:
        return GitlabService(oauth_token)
    else:
        raise NotImplementedError(f"{oauth_token.provider} is not implemented!")
