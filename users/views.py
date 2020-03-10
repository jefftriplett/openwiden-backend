from authlib.common.errors import AuthlibBaseError
from authlib.integrations.django_client import OAuth
from rest_framework import views, permissions, status, viewsets, mixins
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .exceptions import OAuthProviderNotFound
from .filters import OAuthCompleteFilter
from .serializers import UserSerializer
from .utils import create_or_update_user

oauth = OAuth()
oauth.register("github")


class OAuthLoginView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, provider):
        client = oauth.create_client(provider)

        if client is None:
            raise OAuthProviderNotFound(provider)

        redirect_uri = request.GET.get("redirect_uri")

        return client.authorize_redirect(request, redirect_uri)


class OAuthCompleteView(views.APIView):
    permission_classes = (permissions.AllowAny,)
    filter_backends = (OAuthCompleteFilter,)

    def get(self, request, provider: str):
        client = oauth.create_client(provider)

        if client is None:
            raise OAuthProviderNotFound(provider)

        try:
            token = client.authorize_access_token(request)
            user = self.request.user

            if user.is_anonymous:
                user = create_or_update_user(provider, client, token)

            refresh = RefreshToken.for_user(user)
            jwt = {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }

            msg, code = jwt, status.HTTP_200_OK
        except AuthlibBaseError as e:
            msg, code = e.description, status.HTTP_400_BAD_REQUEST

        return Response({"detail": msg}, code)


class UserViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = UserSerializer
    lookup_field = "id"

    def get_object(self):
        return self.request.user

    def list(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
