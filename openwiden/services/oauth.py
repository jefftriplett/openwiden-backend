import requests
import typing as t
from uuid import uuid4

from authlib.common.errors import AuthlibBaseError
from authlib.integrations.django_client import OAuth, DjangoRemoteApp
from django.contrib.auth.models import AnonymousUser
from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _
from rest_framework.request import Request

from openwiden.users import models
from openwiden import enums, exceptions
from openwiden.services import serializers, models as service_models


# def gitlab_compliance_fix(session):
#     """
#     OAuth fix for Gitlab, because Gitlab does not return expires_at.
#     """
#
#     def _fix(response):
#         token = response.json()
#         token["expires_at"] = 60 * 60 * 24  # 1 day in seconds
#         response._content = to_unicode(json.dumps(token)).encode("utf-8")
#         return response
#
#     session.register_compliance_hook("access_token_response", _fix)


def update_token(vcs, token, refresh_token=None, access_token=None):
    """
    OAuth token update handler for authlib.
    """
    if refresh_token:
        qs = models.VCSAccount.objects.filter(vcs=vcs, refresh_token=refresh_token)
    elif access_token:
        qs = models.VCSAccount.objects.filter(vcs=vcs, access_token=access_token)
    else:
        return None

    if qs.exists():
        oauth_token = qs.first()
        oauth_token.access_token = token["access_token"]
        oauth_token.refresh_token = token["refresh_token"]
        oauth_token.expires_at = token["expires_at"]
        oauth_token.save(update_fields=("access_token", "refresh_token", "expires_at"))


oauth = OAuth(update_token=update_token)
oauth.register("github")
oauth.register("gitlab")  # compliance_fix=gitlab_compliance_fix


class OAuthService:
    @staticmethod
    def get_client(vcs: str) -> DjangoRemoteApp:
        """
        Returns authlib client instance or None if not found.
        """
        client = oauth.create_client(vcs)
        if client is None:
            raise exceptions.ServiceException(_("{vcs} is not found.").format(vcs=vcs))
        return client

    @staticmethod
    def get_token(client: DjangoRemoteApp, request: Request) -> dict:
        """
        Returns token data from provider.
        """
        try:
            return client.authorize_access_token(request)
        except AuthlibBaseError as e:
            raise exceptions.ServiceException(e.description)

    @staticmethod
    def get_profile(vcs: str, request: Request) -> "service_models.Profile":
        """
        Returns profile mapped cls with a data from provider's API.
        """
        client = OAuthService.get_client(vcs)
        token = OAuthService.get_token(client, request)

        try:
            profile_data = client.get("user", token=token).json()

            # Also check if email does not exist and get it from API
            # Useful for GitHub, when "private email" option is ON.
            if profile_data.get("email") is None:
                emails = client.get("user/emails", token=token).json()
                profile_data["email"] = emails[0]["email"]

        except AuthlibBaseError as e:
            raise exceptions.ServiceException(e.description)
        else:
            # Modify raw profile data if needed
            if vcs == enums.VersionControlService.GITHUB:
                serializer = serializers.GitHubUserSerializer(data=profile_data)
            elif vcs == enums.VersionControlService.GITLAB:
                serializer = serializers.GitlabUserSerializer(data=profile_data)
            else:
                raise exceptions.ServiceException(_("{vcs} is not implemented.").format(vcs=vcs))

            # Validate profile data before return
            if serializer.is_valid():
                return service_models.Profile(**serializer.data, **token)
            else:
                raise exceptions.ServiceException(_("Unexpected error occurred."), error=serializer.errors)

    @staticmethod
    def oauth(vcs: str, user: t.Union[models.User, AnonymousUser], request: Request) -> models.User:
        """
        Returns user (new or existed) by provider and service provider profile data.
        """
        profile = OAuthService.get_profile(vcs, request)

        try:
            vcs_account = models.VCSAccount.objects.get(vcs=vcs, remote_id=profile.id)
        except models.VCSAccount.DoesNotExist:
            # Handle case when vcs_account does not exists (first provider auth)
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
            OAuthService.new_vcs_account(
                user=user,
                vcs=vcs,
                remote_id=profile.id,
                login=profile.login,
                access_token=profile.access_token,
                token_type=profile.token_type,
                refresh_token=profile.refresh_token,
                expires_at=profile.expires_at,
            )
            return user
        else:
            # If user is authenticated, then check that vcs_account's user
            # is the same and if not -> just change it for current user.
            # Explanation:
            # github auth -> new user was created -> logout
            # gitlab auth -> new user was created and now we have a two user accounts,
            # but for the same user, that's wrong, because we want to have one account, but for
            # multiple services (github, gitlab etc.).
            # Now, if the second user will repeat auth with github, then vcs_account user will be
            # changed for the second user. Now we have one user account with two oauth_tokens as expected.
            update_fields = ()

            if user.is_authenticated:
                if vcs_account.user.username != user.username:
                    vcs_account.user = user
                    update_fields += ("user",)

            # Change vcs_account login if it's changed in github, gitlab etc.
            if vcs_account.login != profile.login:
                vcs_account.login = profile.login
                update_fields += ("login",)

            # Save changes for vcs_account
            if update_fields:
                vcs_account.save(update_fields=update_fields)

            # Return vcs_account's user, because we can handle case when
            # user is not authenticated, but vcs_account for specified profile does exist.
            return vcs_account.user

    @staticmethod
    def new_vcs_account(
        user: models.User,
        vcs: str,
        remote_id: int,
        login: str,
        access_token: str,
        token_type: str = None,
        refresh_token: str = None,
        expires_at: int = None,
    ):
        """
        Validate specified data and create new oauth token instance.
        Also trigger new actions for a new created token.
        """
        data = dict(
            user=user.id,
            vcs=vcs,
            remote_id=remote_id,
            login=login,
            access_token=access_token,
            token_type=token_type,
            refresh_token=refresh_token,
            expires_at=expires_at,
        )
        s = serializers.OAuthTokenSerializer(data=data)

        # Save vcs account instance
        if s.is_valid():
            return s.save()
        else:
            raise exceptions.ServiceException(str(s.errors))
