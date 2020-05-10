from django.db import models
from django.urls import reverse
from model_utils.models import UUIDModel
from django.utils.translation import gettext_lazy as _
from openwiden.repositories import models as repo_models


class RepositoryWebhook(UUIDModel):
    repository = models.OneToOneField(
        repo_models.Repository, models.CASCADE, related_name="webhook", verbose_name=_("repository")
    )
    remote_id = models.PositiveIntegerField(_("remote id"), blank=True, null=True)

    url = models.URLField(_("url"), blank=True, null=True)
    secret = models.CharField(_("secret"), max_length=40)

    is_active = models.BooleanField(_("is active"), default=False)
    issue_events_enabled = models.BooleanField(_("issue events enabled"), default=False)

    created_at = models.DateTimeField(_("created at"), blank=True, null=True)
    updated_at = models.DateTimeField(_("updated at"), blank=True, null=True)

    class Meta:
        verbose_name = _("webhook")
        verbose_name_plural = _("list of webhooks")

    def __str__(self):
        return _("repository webhook for {repo}").format(repo=self.repository.name)

    def get_absolute_url(self) -> str:
        return reverse("api-v1:repo-webhook-receive", kwargs={"id": self.id})
