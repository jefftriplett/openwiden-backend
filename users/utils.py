from typing import Optional
from uuid import uuid4

from rest_framework.request import Request

from .models import User, OAuth2Token


class Profile:
    def __init__(self, id: str, login: str, name: str, email: str, split_name: bool = True, **kwargs):
        self.id = id
        self.login = login
        self._name = name
        self.email = email
        self.first_name = None
        self.last_name = None

        if split_name:
            self.first_name, sep, self.last_name = self._name.partition(" ")


def get_github_profile(client, token) -> Profile:
    profile_data = client.get("user", token=token).json()
    return Profile(**profile_data)


def get_gitlab_profile(client, token) -> Profile:
    profile_data = client.get("user", token=token).json()
    profile_data["login"] = profile_data.pop("username")
    return Profile(**profile_data)


def get_profile(provider: str, client, token) -> Optional[Profile]:
    if provider == "github":
        return get_github_profile(client, token)
    elif provider == "gitlab":
        return get_gitlab_profile(client, token)
    else:
        return None


def create_or_update_user(provider: str, client, request: Request):
    token = client.authorize_access_token(request)
    profile: Profile = get_profile(provider, client, token)
    user = None

    try:
        oauth2_token = OAuth2Token.objects.get(provider=provider, remote_id=profile.id)

        if request.user.is_authenticated:
            if oauth2_token.user != request.user:
                oauth2_token.user = request.user

        if oauth2_token.login != profile.login:
            oauth2_token.login = profile.login

        oauth2_token.save()

        user = oauth2_token.user
    except OAuth2Token.DoesNotExist:
        if request.user.is_anonymous:
            qs = User.objects.filter(username=profile.login)
            if qs.exists():
                profile.login = f"{profile.login}_{uuid4().hex}"

            user = User.objects.create(
                username=profile.login, email=profile.email, first_name=profile.first_name, last_name=profile.last_name,
            )

        OAuth2Token.objects.create(
            user=user,
            provider=provider,
            remote_id=profile.id,
            login=profile.login,
            access_token=token["access_token"],
            token_type=token.get("token_type", ""),
            refresh_token=token.get("refresh_token", ""),
            expires_at=token.get("expires_at"),
        )

    return user
