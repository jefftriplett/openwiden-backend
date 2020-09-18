from . import models, exceptions


def find_vcs_account(user: models.User, vcs: str) -> models.VCSAccount:
    """
    Returns version control service account by specified user and vcs name.
    """
    try:
        vcs_account = models.VCSAccount.objects.get(user=user, vcs=vcs)
    except models.VCSAccount.DoesNotExist:
        raise exceptions.VCSAccountDoesNotExist(vcs=vcs)
    else:
        return vcs_account
