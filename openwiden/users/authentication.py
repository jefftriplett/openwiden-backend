from typing import Tuple

from django.utils.translation import gettext_lazy as _

from rest_framework import authentication, exceptions
from rest_framework.authentication import get_authorization_header

from .models import User


class GitHubOAuth(authentication.BaseAuthentication):
    keyword = "Token"

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _("Invalid token header. No credentials provided.")
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _("Invalid token header. Token string should not contain spaces.")
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _("Invalid token header. " "Token string should not contain invalid characters.")
            raise exceptions.AuthenticationFailed(msg)

        return self.get_user(token)

    @staticmethod
    def get_user(token) -> Tuple[User, None]:
        try:
            user = User.objects.get(github_token=token)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed(_("Invalid token."))

        if not user.is_active:
            raise exceptions.AuthenticationFailed(_("User inactive or deleted."))

        return user, None
