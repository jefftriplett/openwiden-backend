from django.utils.translation import gettext_lazy as _
from django.db import models


class VersionControlService(models.TextChoices):
    GITHUB = "github", _("GitHub")
    GITLAB = "gitlab", _("Gitlab")
