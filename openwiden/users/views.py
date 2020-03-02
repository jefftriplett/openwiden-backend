from django.http import HttpResponseRedirect
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.permissions import AllowAny

from openwiden.users import github_oauth
from .models import User
from .serializers import UserSerializer, GitHubOAuthCodeSerializer, CreateUserSerializer
from django.conf import settings
from django.utils.translation import gettext_lazy as _


github = github_oauth.GitHubOAuth(
    settings.GITHUB_KEY, settings.GITHUB_SECRET, ["user:email"]
)


class GitHubOAuthAPIException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Invalid input.")
    default_code = "invalid"


class UserViewSet(viewsets.ModelViewSet):
    """
    User view set.
    """

    serializer_classes = {
        "default": UserSerializer,
        "create": GitHubOAuthCodeSerializer,
    }
    queryset = User.objects.all()
    lookup_field = "id"

    def get_serializer_class(self):
        return self.serializer_classes.get(
            self.action, self.serializer_classes["default"]
        )

    def get_permissions(self):
        if self.action in ["create", "auth"]:
            return [AllowAny()]
        return super().get_permissions()

    def perform_create(self, serializer):
        code = serializer.validated_data["code"]

        try:
            token = github.fetch_token(code)
        except github_oauth.GitHubOAuthException as e:
            raise GitHubOAuthAPIException(e)

        create_serializer = CreateUserSerializer(data={"github_token": token})
        create_serializer.is_valid()
        return create_serializer.save()

    @action(detail=False, methods=["GET"], url_name="auth")
    def auth(self, request, *args, **kwargs):
        return HttpResponseRedirect(github.authorization_url)
