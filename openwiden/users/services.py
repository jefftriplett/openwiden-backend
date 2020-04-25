import requests
import typing as t
from uuid import uuid4

from authlib.integrations.django_client import OAuth, DjangoRemoteApp
from django.core.files.base import ContentFile
from rest_framework.request import Request
from rest_framework_simplejwt.tokens import RefreshToken

from openwiden.users import models

oauth = OAuth()
oauth.register("github")
oauth.register("gitlab")


class Profile:
    def __init__(
        self,
        id: str,
        login: str,
        name: str,
        email: str,
        avatar_url: str,
        access_token: str,
        expires_at,
        split_name: bool = True,
        token_type: str = None,
        refresh_token: str = None,
        **kwargs,
    ):
        self.id = id
        self.login = login
        self._name = name
        self.email = email
        self.first_name = None
        self.last_name = None
        self.avatar_url = avatar_url
        self.access_token = access_token
        self.token_type = token_type
        self.refresh_token = refresh_token
        self.expires_at = expires_at

        if split_name:
            self.first_name, sep, self.last_name = self._name.partition(" ")


class OAuthService:
    @staticmethod
    def get_token(provider: str, request: Request) -> dict:
        """
        Returns token data from provider.
        """
        client = OAuthService.get_client(provider)
        return client.authorize_access_token(request)

    @staticmethod
    def get_profile(provider: str, client: DjangoRemoteApp, request: Request) -> "Profile":
        """
        Returns profile mapped cls with a data from provider's API.
        """
        token = OAuthService.get_token(provider, request)
        profile_data = client.get("user", token=token).json()

        # Modify raw profile data if needed
        if provider == models.OAuth2Token.GITHUB_PROVIDER:
            # Do nothing
            pass
        elif provider == models.OAuth2Token.GITLAB_PROVIDER:
            profile_data["login"] = profile_data.pop("username")
        else:
            raise NotImplementedError(f"{provider} is not implemented")

        return Profile(**profile_data, **token)

    @staticmethod
    def get_client(provider: str) -> t.Optional[DjangoRemoteApp]:
        """
        Returns authlib client instance or None if not found.
        """
        return oauth.create_client(provider)

    @staticmethod
    def oauth(provider: str, user: models.User, profile: Profile) -> models.User:
        """
        Returns user (new or existed) by provider and service provider profile data.
        """
        try:
            oauth2_token = models.OAuth2Token.objects.get(provider=provider, remote_id=profile.id)
        except models.OAuth2Token.DoesNotExist:
            # Handle case when oauth_token does not exists (first provider auth)
            # Check if user is not authenticated and create it first.
            if user.is_anonymous:
                # Check if username is already exists with profile's login
                # and create unique (login + hex) if exists else do nothing.
                qs = models.User.objects.filter(username=profile.login)
                if qs.exists():
                    profile.login = f"{profile.login}_{uuid4().hex}"

                # Download user's avatar from service
                avatar = ContentFile(requests.get(profile.avatar_url).content)

                # Create new user and save avatar
                user = models.User.objects.create(
                    username=profile.login,
                    email=profile.email,
                    first_name=profile.first_name,
                    last_name=profile.last_name,
                )
                user.avatar.save(f"{uuid4()}.jpg", avatar)

            # Create new oauth token instance for user:
            # New if anonymous or existed if is authenticated.
            models.OAuth2Token.objects.create(
                user=user,
                provider=provider,
                remote_id=profile.id,
                login=profile.login,
                access_token=profile.access_token,
                token_type=profile.token_type or "",
                refresh_token=profile.refresh_token or "",
                expires_at=profile.expires_at,
            )
            return user
        else:
            # If user is authenticated, then check that oauth_token's user
            # is the same and if not -> just change it for current user.
            # Explanation:
            # github auth -> new user was created -> logout
            # gitlab auth -> new user was created and now we have a two user accounts,
            # but for the same user, that's wrong, because we want to have one account, but for
            # multiple services (github, gitlab etc.).
            # Now, if the second user will repeat auth with github, then oauth_token user will be
            # changed for the second user. Now we have one user account with two oauth_tokens as expected.
            if user.is_authenticated:
                if oauth2_token.user.id != user.id:
                    oauth2_token.user = user

            # Change oauth_token login if it's changed in github, gitlab etc.
            if oauth2_token.login != profile.login:
                oauth2_token.login = profile.login

            # Save changes for oauth_token
            oauth2_token.save()

            # Return oauth_token's user, because we can handle case when
            # user is not authenticated, but oauth_token for specified profile does exist.
            return oauth2_token.user


class UserService:
    @staticmethod
    def get_jwt(user: models.User) -> dict:
        """
        Returns JWT tokens for specified user.
        """
        refresh = RefreshToken.for_user(user)
        return dict(access=str(refresh.access_token), refresh=str(refresh))
