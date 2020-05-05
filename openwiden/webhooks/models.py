from django.db import models
from model_utils.models import UUIDModel
from django.utils.translation import gettext_lazy as _
from openwiden.repositories import models as repo_models


class RepositoryWebhook(UUIDModel):
    repository = models.OneToOneField(repo_models.Repository, models.CASCADE, verbose_name=_("repository"))
    remote_id = models.PositiveIntegerField(_("remote id"))

    url = models.URLField(_("url"))
    secret = models.CharField(_("secret"), max_length=40)

    issue_events_enabled = models.BooleanField(_("issue events enabled"))

    created_at = models.DateTimeField(_("created at"), blank=True, null=True)
    updated_at = models.DateTimeField(_("updated at"), blank=True, null=True)

    class Meta:
        verbose_name = _("webhook")
        verbose_name_plural = _("list of webhooks")
        constraints = (models.UniqueConstraint(fields=("repository", "remote_id"), name="unique_repository_webhook"),)

    def __str__(self):
        return _("repository webhook for {repo}").format(repo=self.repository.name)
