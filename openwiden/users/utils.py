from typing import Optional
from uuid import uuid4

import requests
from django.core.files.base import ContentFile
from rest_framework.request import Request

from . import models


class Profile:
    def __init__(self, id: str, login: str, name: str, email: str, avatar_url: str, split_name: bool = True, **kwargs):
        self.id = id
        self.login = login
        self._name = name
        self.email = email
        self.first_name = None
        self.last_name = None
        self.avatar_url = avatar_url

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
    user = request.user

    try:
        oauth2_token = models.OAuth2Token.objects.get(provider=provider, remote_id=profile.id)

        if request.user.is_authenticated:
            if oauth2_token.user.username != request.user.username:
                oauth2_token.user = request.user

        if oauth2_token.login != profile.login:
            oauth2_token.login = profile.login

        oauth2_token.save()

        user = oauth2_token.user
    except models.OAuth2Token.DoesNotExist:
        if request.user.is_anonymous:
            qs = models.User.objects.filter(username=profile.login)
            if qs.exists():
                profile.login = f"{profile.login}_{uuid4().hex}"

            avatar = ContentFile(requests.get(profile.avatar_url).content)

            user = models.User.objects.create(
                username=profile.login, email=profile.email, first_name=profile.first_name, last_name=profile.last_name,
            )
            user.avatar.save(f"{uuid4()}.jpg", avatar)

        models.OAuth2Token.objects.create(
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
