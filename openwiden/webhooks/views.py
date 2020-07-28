from rest_framework.generics import get_object_or_404

from . import selectors

from github_webhooks.views import GitHubWebhookView as BaseGitHubWebhookView
from gitlab_webhooks.views import WebhookView as BaseGitlabWebhookView


class GithubWebhookView(BaseGitHubWebhookView):
    def get_secret(self) -> str:
        return get_object_or_404(selectors.get_webhooks(), id=self.kwargs["id"]).secret


class GitlabWebhookView(BaseGitlabWebhookView):
    def get_secret(self) -> str:
        return get_object_or_404(selectors.get_webhooks(), id=self.kwargs["id"]).secret
