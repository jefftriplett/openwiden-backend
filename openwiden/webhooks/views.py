from rest_framework.generics import get_object_or_404

from . import models, selectors

from github_webhooks import views as github_webhook_views


__all__ = ("github_webhook_view",)


class GithubWebhookView(github_webhook_views.GitHubWebhookView):
    def get_secret(self) -> str:
        webhook: models.RepositoryWebhook = get_object_or_404(
            selectors.get_webhooks(), id=self.kwargs["id"],
        )
        return webhook.secret


github_webhook_view = GithubWebhookView.as_view()
