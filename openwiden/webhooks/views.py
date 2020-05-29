from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import views, permissions, renderers, parsers
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request

from openwiden.services import get_service
from openwiden.webhooks import services


@method_decorator(csrf_exempt, "dispatch")
class RepositoryWebhookView(views.APIView):
    permission_classes = (permissions.AllowAny,)
    renderer_classes = (renderers.JSONRenderer,)
    parser_classes = (parsers.JSONParser,)

    def post(self, request: Request, id: str):
        webhook = get_object_or_404(services.RepositoryWebhook.all(), id=id)
        return get_service(vcs=webhook.repository.vcs).handle_webhook(webhook, request)


repository_webhook_view = RepositoryWebhookView.as_view()
