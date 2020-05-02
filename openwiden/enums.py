from django.utils.translation import gettext_lazy as _
from django.db import models


class VersionControlService(models.TextChoices):
    GITHUB = "github", _("GitHub")
    GITLAB = "gitlab", _("Gitlab")


class VisibilityLevel(models.TextChoices):
    public = "public", _("public")
    private = "private", _("private")
    internal = "internal", _("internal")
