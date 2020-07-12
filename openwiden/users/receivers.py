from django.db.models.signals import post_save
from django.dispatch import receiver

from openwiden.users import models


@receiver(post_save, sender=models.VCSAccount)
def new_vcs_account(instance: models.VCSAccount, created: bool, **kwargs):
    if created:
        pass
