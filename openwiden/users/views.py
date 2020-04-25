from authlib.common.errors import AuthlibBaseError
from authlib.integrations.django_client import DjangoRemoteApp

from rest_framework import views, permissions as drf_permissions, status, viewsets, mixins
from rest_framework.response import Response

from openwiden.users import exceptions, filters, models, permissions, serializers, services


class OAuthView(views.APIView):
    """
    Base oauth view for inheritance by login and complete views.
    """

    permission_classes = (drf_permissions.AllowAny,)

    @staticmethod
    def get_client(provider: str) -> DjangoRemoteApp:
        """
        Returns client or raises OAuthProviderNotFound exception.
        """
        client: DjangoRemoteApp = services.OAuthService.get_client(provider)
        if client is None:
            raise exceptions.OAuthProviderNotFound(provider)
        return client


class OAuthLoginView(OAuthView):
    """
    Redirects user for auth via available provider.

    # GitLab
    For GitLab `redirect_uri` is required.
    GitLab tries to find redirect_uri from the list, specified in the app `Callback URL` settings.
    This is why if redirect_uri was not specified in the query parameters, an error will occur from GitLab.

    For example:
    ### http://0.0.0.0:8000/users/login/gitlab/?redirect_uri=http://0.0.0.0:8000/users/complete/gitlab/
    """

    def get(self, request, provider):
        client: DjangoRemoteApp = self.get_client(provider)

        redirect_uri = request.GET.get("redirect_uri")

        # GitLab OAuth requires redirect_uri,
        # that's why additional check should be passed
        if provider == "gitlab":
            if redirect_uri is None:
                raise exceptions.GitLabOAuthMissedRedirectURI()

        return client.authorize_redirect(request, redirect_uri)


oauth_login_view = OAuthLoginView.as_view()


class OAuthCompleteView(OAuthView):
    """
    Creates or updates user for specified provider.
    """

    filter_backends = (filters.OAuthCompleteFilter,)

    def get(self, request, provider: str):
        client: DjangoRemoteApp = self.get_client(provider)

        # If no specified provider found
        if client is None:
            raise exceptions.OAuthProviderNotFound(provider)

        # Return user (new or created) for specified provider profile.
        try:
            profile: services.Profile = services.OAuthService.get_profile(provider, client, request)
        except AuthlibBaseError as e:
            return Response({"detail": e.description}, status.HTTP_400_BAD_REQUEST)
        else:
            # TODO: handle requests error or skip avatar download
            user = services.OAuthService.oauth(provider, self.request.user, profile)
            jwt_tokens = services.UserService.get_jwt(user)
            return Response(jwt_tokens)


oauth_complete_view = OAuthCompleteView.as_view()


class UserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.UserSerializer
    lookup_field = "id"
    queryset = models.User.objects.all()
    permission_classes = (permissions.IsUserOrAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return serializers.UserUpdateSerializer
        return super().get_serializer_class()


class UserByTokenView(views.APIView):
    """
    Returns current user's oauth tokens.
    """

    def get(self, request):
        data = serializers.UserWithOAuthTokensSerializer(instance=request.user).data
        return Response(data=data)


user_by_token_view = UserByTokenView.as_view()
