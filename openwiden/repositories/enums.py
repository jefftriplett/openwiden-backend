from django.db import models
from django.utils.translation import gettext_lazy as _


class VisibilityLevel(models.TextChoices):
    public = "public", _("public")
    private = "private", _("private")
    internal = "internal", _("internal")
