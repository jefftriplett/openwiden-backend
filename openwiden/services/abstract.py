import typing as t
from abc import ABC, abstractmethod
from uuid import uuid4

import requests
from authlib.common.errors import AuthlibBaseError
from authlib.integrations.django_client import OAuth, DjangoRemoteApp
from django.contrib.auth.models import AnonymousUser
from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _
from rest_framework.request import Request
from rest_framework.response import Response

from openwiden.services import serializers, models as service_models
from openwiden.users import models as users_models
from openwiden.repositories import services as repo_services
from openwiden.repositories import models as repo_models
from openwiden.organizations import services as org_services
from openwiden.organizations import models as org_models
from openwiden.webhooks import services as webhook_services
from openwiden.webhooks import models as webhook_models
from openwiden import exceptions


def update_token(vcs, token, refresh_token=None, access_token=None):
    """
    OAuth token update handler for authlib.
    """
    if refresh_token:
        qs = users_models.VCSAccount.objects.filter(vcs=vcs, refresh_token=refresh_token)
    elif access_token:
        qs = users_models.VCSAccount.objects.filter(vcs=vcs, access_token=access_token)
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
oauth.register("gitlab")


class RemoteService(ABC):
    """
    Abstract class for all services implementation.
    """

    repo_sync_serializer: t.Type[serializers.RepositorySync] = None
    org_sync_serializer: t.Type[serializers.OrganizationSync] = None
    issue_sync_serializer: t.Type[serializers.IssueSync] = None
    user_profile_serializer: t.Type[serializers.UserProfileSerializer] = None

    def __init__(self, *, vcs_account: users_models.VCSAccount = None, vcs: str = None):
        assert (vcs_account or vcs) or not (vcs_account and vcs), "vcs_account or vcs should be specified."

        if vcs_account:
            self.vcs_account = vcs_account
            self.vcs = vcs_account.vcs
            self.token = self.vcs_account.to_token()
        elif vcs:
            self.vcs = vcs

        self.client = self.get_client()

    def get_client(self) -> DjangoRemoteApp:
        """
        Returns authlib client instance or None if not found.
        """
        client = oauth.create_client(self.vcs)
        if client is None:
            raise exceptions.ServiceException(_("{vcs} is not found.").format(vcs=self.vcs))
        return client

    def get_token(self, request: Request) -> dict:
        """
        Returns token data from provider.
        """
        try:
            return self.client.authorize_access_token(request)
        except AuthlibBaseError as e:
            raise exceptions.ServiceException(e.description)

    def get_profile(self, request: Request) -> "service_models.Profile":
        """
        Returns profile mapped cls with a data from provider's API.
        """
        self.token = self.get_token(request)

        try:
            profile_data = self.client.get("user", token=self.token).json()

            # Also check if email does not exist and get it from API
            # Useful for GitHub, when "private email" option is ON.
            if profile_data.get("email") is None:
                emails = self.client.get("user/emails", token=self.token).json()
                profile_data["email"] = emails[0]["email"]

        except AuthlibBaseError as e:
            raise exceptions.ServiceException(e.description)
        else:
            serializer = self.user_profile_serializer(data=profile_data)

            # Validate profile data before return
            if serializer.is_valid():
                return service_models.Profile(**serializer.data, **self.token)
            else:
                raise exceptions.ServiceException(_("Unexpected error occurred."), error=serializer.errors)

    @abstractmethod
    def parse_org_slug(self, repo_data: dict) -> t.Optional[str]:
        """
        Returns repository organization id or None if repository owner is user.
        """
        pass

    @abstractmethod
    def get_user_repos(self) -> t.List[dict]:
        """
        Returns repository data by calling remote API.
        """
        pass

    @abstractmethod
    def get_repo_languages(self, repo: repo_models.Repository) -> dict:
        """
        Returns repository languages data by calling remote API.
        """
        pass

    @abstractmethod
    def get_repo_issues(self, repo: repo_models.Repository) -> t.List[dict]:
        """
        Returns repository issues data by calling remote API.
        """
        pass

    @abstractmethod
    def get_org(self, slug: str) -> dict:
        """
        Returns organization data by slug field.
        GitHub: name.
        Gitlab: id.
        """
        pass

    @abstractmethod
    def check_org_membership(self, organization: org_models.Organization) -> t.Tuple[bool, bool]:
        """
        Checks organization membership for a current user and returns tuple: is_member & is_admin.
        """
        pass

    def sync(self) -> None:
        """
        Synchronizes user's repositories and organizations.
        """
        repositories_data = self.get_user_repos()
        for data in repositories_data:

            # Check if serializer is valid and try to save repository.
            serializer = self.repo_sync_serializer(data=data)
            if serializer.is_valid():
                repository_kwargs = dict(vcs=self.vcs, **serializer.validated_data)

                # Sync organization or just add user as owner
                organization_slug = self.parse_org_slug(data)
                if organization_slug:
                    organization = self.sync_org(slug=organization_slug)
                    repository_kwargs["organization"] = organization
                else:
                    repository_kwargs["owner"] = self.vcs_account

                # Sync repository locally
                repo_services.Repository.sync(**repository_kwargs)
            else:
                raise exceptions.ServiceException(
                    _("an error occurred while synchronizing repository, please, try again.")
                )

    def sync_repo(self, repo: repo_models.Repository):
        """
        Synchronizes repository.
        """
        self.sync_repo_issues(repo)
        self.sync_repo_webhook(repo)
        repo.programming_languages = self.get_repo_languages(repo)
        repo.save(update_fields=("programming_languages", "is_added"))

    def sync_repo_issues(self, repo: repo_models.Repository):
        """
        Synchronizes repository issues.
        """
        issues = self.get_repo_issues(repo)

        if issues:
            serializer = self.issue_sync_serializer(data=issues, many=True)
            if serializer.is_valid():
                for data in serializer.validated_data:
                    repo_services.Issue.sync(repo, **data)
            else:
                raise exceptions.ServiceException(
                    _("an error occurred while synchronizing issues, please, try again. Errors: {e}").format(
                        e=serializer.errors
                    )
                )

    @abstractmethod
    def create_repo_webhook(self, webhook: webhook_models.RepositoryWebhook):
        pass

    @abstractmethod
    def update_repo_webhook(self, webhook: webhook_models.RepositoryWebhook):
        pass

    @abstractmethod
    def repo_webhook_exist(self, repo: repo_models.Repository, webhook_id: int) -> bool:
        pass

    def sync_repo_webhook(self, repo: repo_models.Repository):
        """
        Synchronizes repository webhook.
        """
        webhook, created = webhook_services.RepositoryWebhook.get_or_create(repo)
        if created:
            self.create_repo_webhook(webhook)
        else:
            if webhook.remote_id:
                if self.repo_webhook_exist(repo, webhook.remote_id):
                    self.update_repo_webhook(webhook)
            else:
                self.create_repo_webhook(webhook)

    def sync_org(self, *, org: org_models.Organization = None, slug: str = None):
        """
        Synchronizes organization by instance or slug.
        """
        assert org or slug, "organization instance or slug should be specified."

        # Get organization data and pass for validate
        org_data = self.get_org(slug or org.name)
        org_serializer = self.org_sync_serializer(data=org_data)

        if org_serializer.is_valid():
            organization = org_services.Organization.sync(vcs=self.vcs, **org_serializer.validated_data)[0]

            # Sync organization and membership for a current user
            self.sync_org_membership(organization)
        else:
            raise exceptions.ServiceException(
                _("an error occurred while synchronizing organization, please, try again.")
            )

        return organization

    def sync_org_membership(self, organization: org_models.Organization) -> None:
        """
        Synchronizes organization membership for a current user.
        """
        is_member, is_admin = self.check_org_membership(organization)

        if is_member:
            org_services.Member.sync(organization, self.vcs_account, is_admin)
        else:
            org_services.Organization.remove_member(organization, self.vcs_account)

    @classmethod
    @abstractmethod
    def handle_webhook(cls, webhook: webhook_models.RepositoryWebhook, request: Request) -> Response:
        pass

    @classmethod
    @abstractmethod
    def handle_issue_event(cls, webhook: webhook_models.RepositoryWebhook, data):
        pass

    def oauth(self, user: t.Union[users_models.User, AnonymousUser], request: Request) -> users_models.User:
        """
        Returns user (new or existed) by provider and service provider profile data.
        """
        profile = self.get_profile(request)

        try:
            vcs_account = users_models.VCSAccount.objects.get(vcs=self.vcs, remote_id=profile.id)
        except users_models.VCSAccount.DoesNotExist:
            # Handle case when vcs_account does not exists (first provider auth)
            # Check if user is not authenticated and create it first.
            if user.is_anonymous:
                # Check if username is already exists with profile's login
                # and create unique (login + hex) if exists else do nothing.
                qs = users_models.User.objects.filter(username=profile.login)
                if qs.exists():
                    profile.login = f"{profile.login}_{uuid4().hex}"

                # Download user's avatar from service
                avatar = ContentFile(requests.get(profile.avatar_url).content)

                # Create new user and save avatar
                user = users_models.User.objects.create(
                    username=profile.login,
                    email=profile.email,
                    first_name=profile.first_name,
                    last_name=profile.last_name,
                )
                user.avatar.save(f"{uuid4()}.jpg", avatar)

            # Create new oauth token instance for user:
            # New if anonymous or existed if is authenticated.
            self.new_vcs_account(
                user=user,
                vcs=self.vcs,
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
            update_fields = ("access_token", "token_type", "refresh_token", "expires_at")

            # Update token data fields
            vcs_account.access_token = profile.access_token
            vcs_account.token_type = profile.token_type
            vcs_account.refresh_token = profile.refresh_token
            vcs_account.expires_at = profile.expires_at

            # Change user if current authenticated user is not equals account user
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

    @classmethod
    def new_vcs_account(
        cls,
        user: users_models.User,
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
