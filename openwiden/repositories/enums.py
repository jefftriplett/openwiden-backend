from django.db import models
from django.utils.translation import gettext_lazy as _


class IssueState(models.TextChoices):
    OPEN = "open", _("Open")
    CLOSED = "closed", _("Closed")
