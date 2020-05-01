from openwiden.users import models
from openwiden import enums
from .abstract import ExternalAPIRepositoryService
from openwiden.repositories.services import external


def get_service(oauth_token: models.OAuth2Token) -> ExternalAPIRepositoryService:
    """
    Returns repositories external API class depends on specified oauth_token.
    """
    if oauth_token.provider == enums.VersionControlService.GITHUB:
        return external.GitHubRepositoryService(oauth_token)
    elif oauth_token.provider == enums.VersionControlService.GITLAB:
        return external.GitlabRepositoryService(oauth_token)
    else:
        raise NotImplementedError(f"{oauth_token.provider} is not implemented!")
