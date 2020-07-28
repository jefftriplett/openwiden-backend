from django.db import models
from model_utils.models import UUIDModel
from django.utils.translation import gettext_lazy as _

from openwiden import enums
from openwiden.users.models import VCSAccount


class Organization(UUIDModel):
    vcs = models.CharField(_("version control service"), max_length=50, choices=enums.VersionControlService.choices)
    remote_id = models.PositiveIntegerField(_("remote id"))
    name = models.CharField(_("name"), max_length=255)
    description = models.CharField(_("description"), max_length=255, blank=True, null=True)

    url = models.URLField(_("url"), blank=True, null=True)
    avatar_url = models.URLField(_("avatar url"), blank=True, null=True)

    created_at = models.DateTimeField(_("created at"), blank=True, null=True)

    visibility = models.CharField(
        max_length=8,
        blank=True,
        choices=enums.VisibilityLevel.choices,
        default=enums.VisibilityLevel.public,
        verbose_name=_("visibility"),
    )

    class Meta:
        ordering = ("name",)
        verbose_name = _("organization")
        verbose_name_plural = _("list of organizations")
        constraints = (models.UniqueConstraint(fields=("vcs", "remote_id",), name="unique_org"),)

    def __str__(self):
        return self.name


class Member(UUIDModel):
    organization = models.ForeignKey(Organization, models.CASCADE, "members", "member", verbose_name=_("organization"))
    vcs_account = models.ForeignKey(
        VCSAccount,
        models.CASCADE,
        "org_memberships",
        "org_membership",
        verbose_name=_("version control service account"),
    )

    is_admin = models.BooleanField(_("has admin permissions"), default=False)

    class Meta:
        order_with_respect_to = "organization"
        verbose_name = _("member")
        verbose_name_plural = _("list of members")
        constraints = (models.UniqueConstraint(fields=("vcs_account", "organization"), name="unique_member"),)

    def __str__(self):
        return self.vcs_account.login
