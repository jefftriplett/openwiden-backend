from django.db import models
from django.utils.translation import gettext_lazy as _


class IssueState(models.TextChoices):
    OPEN = "open", _("Open")
    CLOSED = "closed", _("Closed")


class RepositoryState(models.TextChoices):
    INITIAL = "initial", _("initial")
    ADDING = "adding", _("adding")
    ADDED = "added", _("added")
    REMOVING = "removing", _("removing")
    REMOVED = "removed", _("removed")
    ADD_FAILED = "add_failed", _("add failed")
    REMOVE_FAILED = "remove_failed", _("remove failed")
