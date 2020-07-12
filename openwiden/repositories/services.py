import typing as t
from datetime import datetime

from django.db.models import QuerySet

from openwiden import enums, exceptions, vcs_clients
from openwiden.repositories import models, error_messages
from openwiden.users import models as users_models, selectors as users_selectors
from openwiden.organizations import models as organizations_models
from openwiden.vcs_clients.github.models import OwnerType, MembershipType
from openwiden.webhooks import services as webhooks_services


class Repository:
    @staticmethod
    def sync(
        vcs: str,
        remote_id: int,
        name: str,
        url: str,
        created_at: datetime,
        updated_at: datetime,
        description: str = None,
        owner: users_models.User = None,
        organization: organizations_models.Organization = None,
        stars_count: int = 0,
        open_issues_count: int = 0,
        forks_count: int = 0,
        programming_languages: dict = None,
        visibility: str = enums.VisibilityLevel.private,
    ) -> t.Tuple[models.Repository, bool]:
        """
        Synchronizes repository with specified data (update or create).
        """
        fields = dict(
            name=name,
            url=url,
            description=description,
            owner=owner,
            organization=organization,
            stars_count=stars_count,
            open_issues_count=open_issues_count,
            forks_count=forks_count,
            programming_languages=programming_languages,
            visibility=visibility,
            created_at=created_at,
            updated_at=updated_at,
        )

        # Try to create or update repository
        try:
            repository = models.Repository.objects.get(vcs=vcs, remote_id=remote_id)
        except models.Repository.DoesNotExist:
            repository = models.Repository.objects.create(vcs=vcs, remote_id=remote_id, is_added=False, **fields,)
            created = True
        else:
            # Update values if repository exist
            for k, v in fields.items():
                setattr(repository, k, v)
            repository.save(update_fields=fields.keys())
            created = False

        # TODO: notify
        if created:
            pass

        return repository, created

    @staticmethod
    def added(visibility: str = enums.VisibilityLevel.public) -> QuerySet:
        """
        Returns repositories QuerySet filtered by "is_added" field and optional visibility (default is public).
        """
        return models.Repository.objects.filter(is_added=True, visibility=visibility)

    @classmethod
    def get_added_and_public_(cls) -> QuerySet:
        """
        Returns added and public visible repositories also known as "OpenWiden".
        """
        return cls.added(enums.VisibilityLevel.public)


def delete_by_remote_id(*, remote_id: str):
    """
    Finds and deletes repository issue by id.
    """
    models.Issue.objects.filter(remote_id=remote_id).delete()


def add_repository(*, repository: models.Repository, user: users_models.User) -> None:
    """
    Adds existed repository by sync related objects (issues, for example) and changes
    status to "is_added".
    """
    vcs_account = users_selectors.find_vcs_account(user, repository.vcs)

    # Check if repository is already added and raise an error if yes
    if repository.is_added:
        raise exceptions.ServiceException(error_messages.REPOSITORY_ALREADY_ADDED)
    elif repository.visibility == enums.VisibilityLevel.private:
        raise exceptions.ServiceException(error_messages.REPOSITORY_IS_PRIVATE_AND_CANNOT_BE_ADDED)

    # Sync repository and create webhook
    if vcs_account.vcs == enums.VersionControlService.GITHUB:
        github_client = vcs_clients.GitHubClient(vcs_account)
        sync_github_repository(repository_id=repository.remote_id, github_client=github_client)
        webhooks_services.create_github_repository_webhook(
            repository=repository, github_client=github_client,
        )


def remove_repository(*, repository: models.Repository, user: users_models.User) -> None:
    vcs_account = users_selectors.find_vcs_account(user, repository.vcs)

    if repository.is_added is False:
        raise exceptions.ServiceException("repository already removed.")

    if vcs_account.vcs == enums.VersionControlService.GITHUB:
        github_client = vcs_clients.GitHubClient(vcs_account)
        webhooks_services.delete_github_repository_webhook(
            repository=repository, github_client=github_client,
        )

    repository.is_added = False
    repository.save(update_fields=("is_added",))


def sync_github_repository(*, repository_id: int, github_client: vcs_clients.GitHubClient,) -> models.Repository:
    # Sync repository
    repository_data = github_client.get_repository(repository_id=repository_id)
    repository, created = models.Repository.objects.update_or_create(
        remote_id=repository_id,
        vcs=enums.VersionControlService.GITHUB,
        defaults=dict(
            name=repository_data.name,
            description=repository_data.description,
            url=repository_data.url,
            stars_count=repository_data.stargazers_count,
            open_issues_count=repository_data.open_issues_count,
            forks_count=repository_data.forks_count,
            created_at=repository_data.created_at,
            updated_at=repository_data.updated_at,
            visibility=(enums.VisibilityLevel.public if not repository_data.private else enums.VisibilityLevel.private),
        ),
    )

    # Sync repository ownership
    if repository_data.owner.owner_type == OwnerType.ORGANIZATION:
        # Sync organization
        organization = sync_github_organization(
            organization_name=repository_data.owner.login, github_client=github_client,
        )
        repository.organization = organization
    else:
        repository.owner = github_client.vcs_account

    # TODO: service
    # Sync repository issues
    repository_issues = github_client.get_repository_issues(
        owner_name=repository.owner_name, repository_name=repository.name,
    )
    for issue in repository_issues:
        models.Issue.objects.update_or_create(
            repository=repository,
            remote_id=issue.issue_id,
            defaults=dict(
                title=issue.title,
                description=issue.body,
                state=issue.state,
                labels=issue.labels,
                url=issue.html_url,
                created_at=issue.created_at,
                updated_at=issue.updated_at,
                closed_at=issue.closed_at,
            ),
        )

    # Sync repository languages
    repository.programming_languages = github_client.get_repository_languages(
        owner_name=repository.owner_name, repository_name=repository.name
    )

    # Save repository
    repository.is_added = True
    repository.save()

    return repository


# TODO: organization app service
def sync_github_organization(
    *, organization_name: str, github_client: vcs_clients.GitHubClient,
) -> organizations_models.Organization:
    organization_data = github_client.get_organization(organization_name=organization_name)

    organization, created = organizations_models.Organization.objects.update_or_create(
        vcs=enums.VersionControlService.GITHUB,
        remote_id=organization_data.organization_id,
        defaults=dict(
            name=organization_data.login,
            description=organization_data.description,
            url=organization_data.html_url,
            avatar_url=organization_data.avatar_url,
            created_at=organization_data.created_at,
        ),
    )

    # Sync organization membership
    membership_type = github_client.check_organization_membership(organization_name)
    if membership_type == MembershipType.ADMIN:
        sync_member, is_admin = True, True
    elif membership_type == MembershipType.MEMBER:
        sync_member, is_admin = True, False
    else:
        sync_member, is_admin = False, False

    if sync_member:
        organizations_models.Member.objects.update_or_create(
            organization=organization, vcs_account=github_client.vcs_account, defaults=dict(is_admin=is_admin),
        )
    else:
        organization.members.filter(vcs_account=github_client.vcs_account).delete()

    return organization


def sync_github_user_repositories(*, github_client: vcs_clients.GitHubClient) -> None:
    user_repositories = github_client.get_user_repositories()
    for repository in user_repositories:
        sync_github_repository(
            repository_id=repository.repository_id, github_client=github_client,
        )


def sync_user_repositories(*, vcs_account: users_models.VCSAccount) -> None:
    if vcs_account.vcs == enums.VersionControlService.GITHUB:
        github_client = vcs_clients.GitHubClient(vcs_account)
        sync_github_user_repositories(github_client=github_client)
    else:
        raise exceptions.ServiceException(f"vcs {vcs_account.vcs} is not supported yet!")
