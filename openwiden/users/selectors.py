from openwiden import exceptions

from . import models, error_messages


def find_vcs_account(user: models.User, vcs: str) -> models.VCSAccount:
    """
    Returns version control service account by specified user and vcs name.
    """
    try:
        vcs_account = models.VCSAccount.objects.get(user=user, vcs=vcs)
    except models.VCSAccount.DoesNotExist:
        error = error_messages.VCS_ACCOUNT_DOES_NOT_EXIST.format(vcs=vcs)
        raise exceptions.ServiceException(error)
    else:
        return vcs_account
