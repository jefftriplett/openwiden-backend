from django.contrib.postgres.fields import ArrayField
from django.db import models
from model_utils.models import UUIDModel, SoftDeletableModel
from model_utils import Choices
from django.utils.translation import gettext_lazy as _
from openwiden.repositories import managers


class ProgrammingLanguage(models.Model):
    name = models.CharField(_("name"), max_length=100, unique=True)

    class Meta:
        ordering = ("name",)
        verbose_name = _("programming language")
        verbose_name_plural = _("list of programming languages")

    def __str__(self):
        return self.name


class VersionControlService(models.Model):
    name = models.CharField(_("name"), max_length=100)
    host = models.CharField(_("host"), max_length=50, unique=True)

    class Meta:
        ordering = ("host",)
        verbose_name = _("version control service")
        verbose_name_plural = _("version control services")

    def __str__(self):
        return self.name


class Repository(SoftDeletableModel, UUIDModel):
    version_control_service = models.ForeignKey(
        VersionControlService, models.PROTECT, related_name="repositories", verbose_name=_("version control service")
    )
    remote_id = models.PositiveIntegerField(_("remote repository id"))
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), blank=True)
    url = models.URLField(_("url"))

    star_count = models.PositiveIntegerField(_("star count"), default=0)
    open_issues_count = models.PositiveSmallIntegerField(_("open issues count"), default=0)
    forks_count = models.PositiveSmallIntegerField(_("forks count"), default=0)

    created_at = models.DateTimeField(_("created at"))
    updated_at = models.DateTimeField(_("updated at"))

    programming_language = models.ForeignKey(
        ProgrammingLanguage, models.PROTECT, "repositories", "repository", verbose_name=_("programming language")
    )

    objects = managers.Repository()

    class Meta:
        ordering = ("-open_issues_count",)
        verbose_name = _("repository")
        verbose_name_plural = _("repositories")
        constraints = (
            models.UniqueConstraint(fields=["version_control_service", "remote_id"], name="unique_repository",),
        )

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        self.update_open_issues_count(save=False)
        super().save(**kwargs)

    def update_open_issues_count(self, save: bool = True):
        """
        Updates open issues count.
        """
        self.open_issues_count = self.issues.filter(state="open").count()
        if save:
            self.save()


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
    closed_at = models.DateTimeField(_("closed at"), blank=True, null=True)
    updated_at = models.DateTimeField(_("updated at"))

    objects = managers.Issue()

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("issue")
        verbose_name_plural = _("issues")
        constraints = (models.UniqueConstraint(fields=["repository", "remote_id"], name="unique_issue"),)

    def __str__(self):
        return self.title
