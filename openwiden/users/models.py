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


class OAuth2Token(models.Model):
    user = models.ForeignKey(
        User, models.CASCADE, related_name="oauth2_tokens", related_query_name="oauth2_token", verbose_name=_("user")
    )
    provider = models.CharField(_("provider name"), max_length=40, choices=enums.VersionControlService.choices)
    remote_id = models.IntegerField(_("user id from provider site"))
    login = models.CharField(_("login"), max_length=150)
    token_type = models.CharField(_("token type"), blank=True, null=True, max_length=40)
    access_token = models.CharField(_("access token"), max_length=200)
    refresh_token = models.CharField(_("refresh token"), blank=True, null=True, max_length=200)
    expires_at = models.PositiveIntegerField(_("expiration date in seconds"), blank=True, null=True)

    class Meta:
        verbose_name = _("oauth2 token")
        verbose_name_plural = _("oauth2 tokens")
        constraints = (models.UniqueConstraint(fields=("provider", "remote_id"), name="unique_oauth"),)

    def __str__(self):
        return self.access_token

    def to_token(self) -> dict:
        return dict(
            access_token=self.access_token,
            token_type=self.token_type,
            refresh_token=self.refresh_token,
            expires_at=self.expires_at,
        )
