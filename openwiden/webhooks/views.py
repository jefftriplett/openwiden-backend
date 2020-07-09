from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import views, permissions, renderers, parsers
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request

from openwiden.services import get_service
from . import services, models

from github_webhooks import views as github_webhook_views


__all__ = ("github_webhook_view",)


@method_decorator(csrf_exempt, "dispatch")
class RepositoryWebhookView(views.APIView):
    permission_classes = (permissions.AllowAny,)
    renderer_classes = (renderers.JSONRenderer,)
    parser_classes = (parsers.JSONParser,)

    def post(self, request: Request, id: str):
        webhook = get_object_or_404(services.RepositoryWebhook.all(), id=id)
        return get_service(vcs=webhook.repository.vcs).handle_webhook(webhook, request)


repository_webhook_view = RepositoryWebhookView.as_view()


class GithubWebhookView(github_webhook_views.GitHubWebhookView):
    def get_secret(self) -> str:
        webhook: models.RepositoryWebhook = get_object_or_404(
            services.get_webhooks(), id=self.kwargs["id"],
        )
        return webhook.secret


github_webhook_view = GithubWebhookView.as_view()
