import hashlib

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import views, permissions, renderers, parsers, status
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response

from openwiden import enums
from openwiden.services import get_service
from openwiden.webhooks import services


@method_decorator(csrf_exempt, "dispatch")
class RepositoryWebhookView(views.APIView):
    permission_classes = (permissions.AllowAny,)
    renderer_classes = (renderers.JSONRenderer,)
    parser_classes = (parsers.JSONParser,)

    def post(self, request: Request, id: str):
        webhook = get_object_or_404(services.RepositoryWebhook.all(), id=id)
        vcs = webhook.repository.vcs

        if vcs == enums.VersionControlService.GITHUB:
            if "HTTP_X_HUB_SIGNATURE" not in request.META:
                return Response("HTTP_X_HUB_SIGNATURE header is missing.", status=status.HTTP_400_BAD_REQUEST)
            elif "HTTP_X_GITHUB_EVENT" not in request.META:
                return Response("HTTP_X_GITHUB_EVENT header is missing.", status=status.HTTP_400_BAD_REQUEST)

            # Check digest required name and get signature
            digest_name, signature = request.META["HTTP_X_HUB_SIGNATURE"].split("=")
            if digest_name != "sha1":
                return Response(f"{digest_name} is not supported digest.", status=status.HTTP_400_BAD_REQUEST)

            # Validate received signature
            if not services.RepositoryWebhook.compare_signatures(webhook, request.body, hashlib.sha1):
                return Response("Invalid HTTP_X_HUB_SIGNATURE header found.")

            event = request.META["HTTP_X_GITHUB_EVENT"]

            get_service(vcs).handle_webhook_data(webhook, event, request.data)

            return Response(f"Ok {event} / {request.data}")
        elif vcs == enums.VersionControlService.GITLAB:
            token = request.META["HTTP_X_GITLAB_TOKEN"]
            print("secret: ", token)

            event = request.META["HTTP_X_GITLAB_EVENT"]
            get_service(vcs=vcs).handle_webhook_data(webhook, event, request.data)

            return Response(f"Ok", headers={"HTTP_X_HUB_SIGNATURE": token})


repository_webhook_view = RepositoryWebhookView.as_view()
