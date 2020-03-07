from django.contrib.postgres.fields import ArrayField
from django.db import models
from model_utils.models import UUIDModel, SoftDeletableModel
from model_utils import Choices
from django.utils.translation import gettext_lazy as _


class VersionControlService(models.Model):
    name = models.CharField(_("name"), max_length=100, unique=True)
    url = models.URLField(_("url"))

    class Meta:
        verbose_name = _("version control service")
        verbose_name_plural = _("version control services")


class Repository(SoftDeletableModel, UUIDModel):
    version_control_service = models.ForeignKey(
        VersionControlService, models.PROTECT, related_name="repositories", verbose_name=_("version control service")
    )
    remote_id = models.PositiveIntegerField(_("remote repository id"))
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), blank=True)
    url = models.URLField(_("url"))
    forks_count = models.PositiveSmallIntegerField(_("forks count"), default=0)
    star_count = models.PositiveIntegerField(_("star count"), default=0)
    created_at = models.DateTimeField(_("created at"))
    updated_at = models.DateTimeField(_("updated at"))
    open_issues_count = models.PositiveSmallIntegerField(_("open issues count"), default=0)

    class Meta:
        verbose_name = _("repository")
        verbose_name_plural = _("repositories")
        constraints = (
            models.UniqueConstraint(fields=["version_control_service", "remote_id"], name="unique_repository",),
        )


class Issue(UUIDModel):
    STATE_CHOICES = Choices(("open", "Open"), ("closed", "Closed"),)

    repository = models.ForeignKey(
        Repository, models.CASCADE, related_name="issues", related_query_name="issue", verbose_name=_("repository")
    )
    remote_id = models.PositiveIntegerField(_("remote issue id"))

    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"))

    state = models.CharField(_("state"), max_length=30, choices=STATE_CHOICES)
    labels = ArrayField(models.CharField(_("label"), max_length=50))

    url = models.URLField(_("url"))

    created_at = models.DateTimeField(_("crated at"))
    closed_at = models.DateTimeField(_("closed at"), blank=True)
    updated_at = models.DateTimeField(_("updated at"))

    class Meta:
        verbose_name = _("issue")
        verbose_name_plural = _("issues")
        constraints = (models.UniqueConstraint(fields=["repository", "remote_id"], name="unique_issue"),)
