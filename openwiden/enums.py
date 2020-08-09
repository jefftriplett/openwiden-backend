from django.utils.translation import gettext_lazy as _
from django.db import models


class VersionControlService(models.TextChoices):
    GITHUB = "github", _("GitHub")
    GITLAB = "gitlab", _("Gitlab")


class OwnerType(models.TextChoices):
    USER = "user", _("user")
    ORGANIZATION = "organization", _("organization")


class OrganizationMembershipType(models.TextChoices):
    ADMIN = "admin", _("admin")
    MEMBER = "member", _("member")
    NOT_A_MEMBER = "not_a_member", _("no a member")
