from django.http import HttpResponseRedirect
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from openwiden.users import github_oauth
from .models import User
from .serializers import UserSerializer, GitHubOAuthCodeSerializer, CreateUserSerializer
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from github import Github


oauth = github_oauth.GitHubOAuth(**settings.GITHUB_OAUTH_SETTINGS)


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
        return self.serializer_classes.get(self.action, self.serializer_classes["default"])

    def get_permissions(self):
        if self.action in ["create", "auth"]:
            return [AllowAny()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data["code"]

        try:
            token = oauth.fetch_token(code)
            github = Github(token)
            user = github.get_user()
        except github_oauth.GitHubOAuthException as e:
            raise GitHubOAuthAPIException(e)

        data = {
            "login": user.login,
            "name": user.name,
            "email": user.email,
            "github_token": token,
        }

        serializer = CreateUserSerializer(data=data)
        serializer.is_valid()
        serializer.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=["GET"], url_name="auth")
    def auth(self, request, *args, **kwargs):
        return HttpResponseRedirect(oauth.authorization_url)
