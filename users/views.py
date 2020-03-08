from authlib.common.errors import AuthlibBaseError
from authlib.integrations.django_client import OAuth
from rest_framework import views, permissions, status
from rest_framework.response import Response

from .exceptions import OAuthProviderNotFound


oauth = OAuth()
oauth.register("github")
# oauth.register("gitlab")


class OAuthLoginView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        provider = kwargs["provider"]
        client = oauth.create_client(provider)

        if client is None:
            raise OAuthProviderNotFound(provider)

        return client.authorize_redirect(request)


class OAuthCompleteView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        provider = kwargs["provider"]
        client = oauth.create_client(provider)

        if client is None:
            raise OAuthProviderNotFound(provider)

        try:
            token = client.authorize_access_token(request)
            # TODO: create / find user & create token model
            msg, code = token, status.HTTP_200_OK
        except AuthlibBaseError as e:
            msg, code = e.description, status.HTTP_400_BAD_REQUEST

        return Response({"detail": msg}, code)
