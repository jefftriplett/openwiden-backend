from authlib.integrations.django_client import DjangoRemoteApp

from rest_framework import views, permissions as drf_permissions, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework_simplejwt.views import TokenRefreshView

from openwiden import enums
from openwiden.services import OAuthService
from openwiden.users import exceptions, models, permissions, serializers, services

token_refresh_view = TokenRefreshView.as_view()


class OAuthLoginView(views.APIView):
    """
    Redirects user for auth via available provider.

    # GitLab
    For GitLab `redirect_uri` is required.
    GitLab tries to find redirect_uri from the list, specified in the app `Callback URL` settings.
    This is why if redirect_uri was not specified in the query parameters, an error will occur from GitLab.

    For example:
    ### http://0.0.0.0:8000/users/login/gitlab/?redirect_uri=http://0.0.0.0:8000/users/complete/gitlab/
    """

    permission_classes = (drf_permissions.AllowAny,)

    @staticmethod
    def get_client(vcs: str) -> DjangoRemoteApp:
        """
        Returns client or raises VCSNotFound exception.
        """
        return OAuthService.get_client(vcs)

    def get(self, request, vcs):
        client: DjangoRemoteApp = self.get_client(vcs)

        redirect_uri = request.GET.get("redirect_uri")

        # GitLab OAuth requires redirect_uri,
        # that's why additional check should be passed
        if vcs == enums.VersionControlService.GITLAB:
            if redirect_uri is None:
                raise exceptions.GitLabOAuthMissedRedirectURI()

        return client.authorize_redirect(request, redirect_uri=redirect_uri)


oauth_login_view = OAuthLoginView.as_view()


class OAuthCompleteView(views.APIView):
    """
    Creates or updates user for specified provider.
    """

    permission_classes = (drf_permissions.AllowAny,)

    def get(self, request, vcs: str):
        user = OAuthService.oauth(vcs, self.request.user, request)
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

    @action(detail=False)
    def me(self, request):
        """
        Returns current authenticated user's information.
        """
        return Response(serializers.UserWithVCSAccountsSerializer(instance=request.user).data)
