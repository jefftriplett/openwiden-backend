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
    name = models.CharField(_("name"), max_length=255)

    url = models.URLField(_("url"), blank=True, null=True)
    avatar_url = models.URLField(_("avatar url"), blank=True, null=True)

    description = models.CharField(_("description"), max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(_("created at"), blank=True, null=True)
    updated_at = models.DateTimeField(_("updated at"), blank=True, null=True)

    users = models.ManyToManyField(User, "users", "user", verbose_name=_("organization users"))

    class Meta:
        ordering = ("name",)
        verbose_name = _("organization")
        verbose_name_plural = _("list of organizations")
        constraints = (
            models.UniqueConstraint(fields=("version_control_service", "remote_id",), name="unique_organization"),
        )

    def __str__(self):
        return self.name
