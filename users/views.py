from authlib.common.errors import AuthlibBaseError
from authlib.integrations.django_client import OAuth
from rest_framework import views, permissions, status, viewsets, mixins
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .exceptions import OAuthProviderNotFound, CreateOrUpdateUserReturnedNone, GitLabOAuthMissedRedirectURI
from .filters import OAuthCompleteFilter
from .serializers import UserSerializer
from .utils import create_or_update_user

oauth = OAuth()
oauth.register("github")
oauth.register("gitlab")


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

    permission_classes = [permissions.AllowAny]

    def get(self, request, provider):
        client = oauth.create_client(provider)

        if client is None:
            raise OAuthProviderNotFound(provider)

        redirect_uri = request.GET.get("redirect_uri")

        # GitLab OAuth requires redirect_uri,
        # that's why additional check should be passed
        if provider == "gitlab":
            if redirect_uri is None:
                raise GitLabOAuthMissedRedirectURI()

        return client.authorize_redirect(request, redirect_uri)


class OAuthCompleteView(views.APIView):
    """
    Creates or updates user for specified provider.
    """

    permission_classes = (permissions.AllowAny,)
    filter_backends = (OAuthCompleteFilter,)

    def get(self, request, provider: str):
        client = oauth.create_client(provider)

        # If no specified provider found
        if client is None:
            raise OAuthProviderNotFound(provider)

        # Try to retrieve token from provider
        try:
            token = client.authorize_access_token(request)
            user = self.request.user

            # If user from request is not authorized (registration or re-auth)
            if user.is_anonymous:
                user = create_or_update_user(provider, client, token)

            if user is None:
                raise CreateOrUpdateUserReturnedNone()

            # Create JWT tokens for created / updated user
            refresh = RefreshToken.for_user(user)
            jwt_tokens = {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }

            msg, code = jwt_tokens, status.HTTP_200_OK
        except AuthlibBaseError as e:
            msg, code = e.description, status.HTTP_400_BAD_REQUEST

        return Response({"detail": msg}, code)


class UserViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    User view set for retrieve, update or delete user.
    """

    serializer_class = UserSerializer
    lookup_field = "id"
    queryset = UserSerializer.Meta.model.objects.all()


class UserRetrieveByTokenView(views.APIView):
    """
    Returns user by provided JWT tokens.
    """

    def get(self, request, *args, **kwargs):
        data = UserSerializer(instance=request.user).data
        return Response(data=data)
