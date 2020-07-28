from authlib.integrations.django_client import token_update
from django.dispatch import receiver
from openwiden.users import models


@receiver(token_update)
def update_token(name, token, refresh_token=None, access_token=None, **kwargs) -> None:
    if refresh_token:
        qs = models.VCSAccount.objects.filter(vcs=name, refresh_token=refresh_token)
    elif access_token:
        qs = models.VCSAccount.objects.filter(vcs=name, access_token=access_token)
    else:
        return None

    if qs.exists():
        vcs_account = qs.first()
        vcs_account.access_token = token["access_token"]
        vcs_account.refresh_token = token["refresh_token"]
        vcs_account.expires_at = token["expires_at"]
        vcs_account.save(update_fields=("access_token", "refresh_token", "expires_at"))
