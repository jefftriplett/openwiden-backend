from django.db import models
from model_utils.models import UUIDModel
from django.utils.translation import gettext_lazy as _

from openwiden.enums import VersionControlService
from openwiden.users.models import User


class Organization(UUIDModel):
    version_control_service = models.CharField(
        _("version control service"), max_length=50, choices=VersionControlService.choices
    )
    remote_id = models.PositiveIntegerField(_("remote id"))

    url = models.URLField(_("url"))
    avatar_url = models.URLField(_("avatar url"))

    description = models.CharField(_("the description of the company"), max_length=255)
    name = models.CharField(_("the shorthand name of the company"), max_length=255)
    company = models.CharField(_("company name"), max_length=255)
    location = models.CharField(_("location"), max_length=255)
    email = models.EmailField(_("publicity visible email"))

    created_at = models.DateTimeField(_("created at"))

    users = models.ManyToManyField(User, "users", "user", verbose_name=_("organization users"))

    class Meta:
        ordering = ("name",)
        verbose_name = _("organization")
        verbose_name_plural = _("list of organizations")
        constraints = (
            models.UniqueConstraint(fields=("version_control_service", "remote_id",), name="unique_organization"),
        )
