from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from model_utils.models import UUIDModel

from openwiden import enums


class User(AbstractUser, UUIDModel):
    avatar = models.ImageField(_("user avatar"), blank=True, upload_to="avatar")

    class Meta:
        ordering = ["-date_joined"]
        verbose_name = _("user")
        verbose_name_plural = _("users")


class VCSAccount(models.Model):
    user = models.ForeignKey(User, models.CASCADE, "vcs_accounts", "vcs_account", verbose_name=_("user"))
    vcs = models.CharField(_("version control service"), max_length=40, choices=enums.VersionControlService.choices)
    remote_id = models.IntegerField(_("user id from provider site"))
    login = models.CharField(_("login"), max_length=150)

    # OAuth2 token
    token_type = models.CharField(_("token type"), blank=True, null=True, max_length=40)
    access_token = models.CharField(_("access token"), max_length=200)
    refresh_token = models.CharField(_("refresh token"), blank=True, null=True, max_length=200)
    expires_at = models.PositiveIntegerField(_("expiration date in seconds"), blank=True, null=True)

    class Meta:
        verbose_name = _("version control service account")
        verbose_name_plural = _("list of version control service accounts")
        constraints = (models.UniqueConstraint(fields=("vcs", "remote_id"), name="unique_vcs_account"),)

    def __str__(self):
        return self.access_token

    def to_token(self) -> dict:
        """
        Returns OAuth token data as a dict.
        """
        data = dict(access_token=self.access_token, token_type=self.token_type, refresh_token=self.refresh_token,)
        if self.expires_at:
            data["expires_at"] = self.expires_at
        return data
