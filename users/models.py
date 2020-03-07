from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from model_utils.models import UUIDModel


class User(AbstractUser, UUIDModel):
    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
