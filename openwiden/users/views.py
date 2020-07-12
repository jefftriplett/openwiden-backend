from authlib.integrations.django_client import DjangoRemoteApp
from drf_yasg.utils import swagger_auto_schema

from rest_framework import views, permissions as drf_permissions, viewsets, mixins, status
from rest_framework.request import Request
from rest_framework.response import Response

from rest_framework_simplejwt.views import TokenRefreshView as JWTRefreshView

from openwiden import enums
from . import exceptions, models, permissions, serializers, services


class TokenRefreshView(JWTRefreshView):
    """Refresh user token

    Takes a refresh type JSON web token and returns an access type JSON web
    token if the refresh token is valid.
    """

    pass


token_refresh_view = TokenRefreshView.as_view()


class OAuthLoginView(views.APIView):
    """Redirects user for auth via available provider

    # GitLab
    For GitLab `redirect_uri` is required.
    GitLab tries to find redirect_uri from the list, specified in the app `Callback URL` settings.
    This is why if redirect_uri was not specified in the query parameters, an error will occur from GitLab.

    For example:
    ### http://0.0.0.0:8000/users/login/gitlab/?redirect_uri=http://0.0.0.0:8000/users/complete/gitlab/
    """

    permission_classes = (drf_permissions.AllowAny,)

    def get(self, request, vcs):
        client: DjangoRemoteApp = services.get_client(vcs=vcs)

        redirect_uri = request.GET.get("redirect_uri")

        # GitLab OAuth requires redirect_uri,
        # that's why additional check should be passed
        if vcs == enums.VersionControlService.GITLAB:
            if redirect_uri is None:
                raise exceptions.GitLabOAuthMissedRedirectURI()

        return client.authorize_redirect(request, redirect_uri=redirect_uri)


oauth_login_view = OAuthLoginView.as_view()


class OAuthCompleteView(views.APIView):
    """Creates or updates user for specified provider

    Should retrieve default GET params from VCS site redirect.
    """

    permission_classes = (drf_permissions.AllowAny,)

    def get(self, request, vcs: str):
        user = services.oauth(vcs=vcs, user=self.request.user, request=request)
        jwt_tokens = services.get_jwt_tokens(user)
        return Response(jwt_tokens)


oauth_complete_view = OAuthCompleteView.as_view()


class UserViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet,
):
    """Users """

    serializer_class = serializers.UserSerializer
    lookup_field = "id"
    queryset = models.User.objects.all()
    permission_classes = (permissions.IsUserOrAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return serializers.UserUpdateSerializer
        return super().get_serializer_class()


class UserMeView(views.APIView):
    """Get current user

    Returns current user with VCS accounts data.
    """

    @swagger_auto_schema(
        request_body=None, responses={status.HTTP_200_OK: serializers.UserWithVCSAccountsSerializer,},
    )
    def get(self, request: Request) -> Response:
        data = serializers.UserWithVCSAccountsSerializer(request.user).data
        return Response(data)


user_me_view = UserMeView.as_view()
