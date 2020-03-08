from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from model_utils.models import UUIDModel


class User(AbstractUser, UUIDModel):
    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")


class OAuth2Token(models.Model):
    user = models.ForeignKey(
        User, models.CASCADE, related_name="tokens", related_query_name="token", verbose_name=_("user")
    )
    # Fields
    provider = models.CharField(_("provider name"), max_length=40)
    token_type = models.CharField(_("token type"), blank=True, max_length=40)
    access_token = models.CharField(_("access token"), max_length=200)
    refresh_token = models.CharField(_("refresh token"), blank=True, max_length=200)
    expires_at = models.PositiveIntegerField(_("expiration date in seconds"))

    class Meta:
        verbose_name = _("oauth2 token")
        verbose_name_plural = _("oauth2 tokens")

    def __str__(self):
        return self.access_token

    def to_dict(self):
        return {
            "access_token": self.access_token,
            "token_type": self.token_type,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at,
        }
