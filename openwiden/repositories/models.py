from django.contrib.postgres.fields import ArrayField, HStoreField
from django.db import models
from model_utils.models import UUIDModel
from django.utils.translation import gettext_lazy as _

from openwiden import enums
from openwiden.organizations.models import Organization
from openwiden.users.models import VCSAccount
from openwiden.repositories import enums as repo_enums


class Repository(UUIDModel):
    vcs = models.CharField(_("version control service"), max_length=50, choices=enums.VersionControlService.choices)
    remote_id = models.PositiveIntegerField(_("remote repository id"))
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), blank=True, null=True)
    url = models.URLField(_("url"))

    owner = models.ForeignKey(
        VCSAccount, models.SET_NULL, "repositories", "repository", blank=True, null=True, verbose_name=_("owner")
    )
    organization = models.ForeignKey(
        Organization,
        models.SET_NULL,
        "repositories",
        "repository",
        blank=True,
        null=True,
        verbose_name=_("organization"),
    )

    stars_count = models.PositiveIntegerField(_("stars count"), default=0)
    open_issues_count = models.PositiveSmallIntegerField(_("open issues count"), default=0)
    forks_count = models.PositiveSmallIntegerField(_("forks count"), default=0)

    created_at = models.DateTimeField(_("created at"))
    updated_at = models.DateTimeField(_("updated at"))

    programming_languages = HStoreField(verbose_name=_("programming languages"), blank=True, null=True)

    state = models.CharField(
        max_length=13,
        choices=repo_enums.RepositoryState.choices,
        default=repo_enums.RepositoryState.INITIAL,
        verbose_name=_("state"),
    )

    class Meta:
        ordering = ("-open_issues_count",)
        verbose_name = _("repository")
        verbose_name_plural = _("repositories")
        constraints = (models.UniqueConstraint(fields=("vcs", "remote_id",), name="unique_repository",),)

    def __str__(self):
        return self.name

    @property
    def owner_name(self) -> str:
        if self.owner:
            return self.owner.login
        elif self.organization:
            return self.organization.name
        else:
            raise ValueError("repository has no owner!")


class Issue(UUIDModel):
    repository = models.ForeignKey(
        Repository, models.CASCADE, related_name="issues", related_query_name="issue", verbose_name=_("repository")
    )
    remote_id = models.PositiveIntegerField(_("remote issue id"))

    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"), blank=True, null=True)

    state = models.CharField(_("state"), max_length=30, choices=repo_enums.IssueState.choices)
    labels = ArrayField(models.CharField(max_length=50), blank=True, null=True, verbose_name=_("labels"))

    url = models.URLField(_("url"))

    created_at = models.DateTimeField(_("crated at"))
    closed_at = models.DateTimeField(_("closed at"), blank=True, null=True)
    updated_at = models.DateTimeField(_("updated at"))

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("issue")
        verbose_name_plural = _("issues")
        constraints = (models.UniqueConstraint(fields=["repository", "remote_id"], name="unique_issue"),)

    def __str__(self):
        return self.title
