from django_q.tasks import async_task

from openwiden.users import models as users_models
from openwiden.repositories import services


def external_repositories_sync(oauth_token: users_models.OAuth2Token) -> None:
    """
    Gets external repository service depends on specified oauth token and
    executes async tasks for user's repositories sync action.
    """
    service = services.external.get_service(oauth_token)
    async_task(service.sync)
