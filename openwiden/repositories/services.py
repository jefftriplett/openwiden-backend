from typing import Tuple

from openwiden import enums, exceptions, vcs_clients
from openwiden.repositories import models, error_messages
from openwiden.users import models as users_models, selectors as users_selectors
from openwiden.organizations import services as organization_services
from openwiden.organizations import models as organizations_models
from openwiden.vcs_clients.github.models import OwnerType
from openwiden.vcs_clients.gitlab.models.repository import NamespaceKind
from openwiden.webhooks import services as webhooks_services


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
        sync_github_repository(
            repository_id=repository.remote_id, github_client=github_client, is_added=True,
        )
        webhooks_services.create_github_repository_webhook(
            repository=repository, github_client=github_client,
        )
    elif vcs_account.vcs == enums.VersionControlService.GITLAB:
        gitlab_client = vcs_clients.GitlabClient(vcs_account)
        repository_data = gitlab_client.get_repository(repository_id=repository.remote_id)
        programming_languages = gitlab_client.get_repository_programming_languages(repository.remote_id)
        _sync_gitlab_repository(
            repository=repository_data,
            vcs_account=vcs_account,
            extra_defaults=dict(is_added=True, programming_languages=programming_languages,),
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


def sync_user_repositories(*, vcs_account: users_models.VCSAccount, is_new_vcs_account: bool = False,) -> None:
    # Init sync kwargs depends on new vcs account or not
    sync_kwargs = {}
    if is_new_vcs_account:
        sync_kwargs.update(
            {"sync_issues": False, "sync_programming_languages": False, "is_added": False,}
        )

    # Call sync depends on VCS
    if vcs_account.vcs == enums.VersionControlService.GITHUB:
        github_client = vcs_clients.GitHubClient(vcs_account)
        user_repositories = github_client.get_user_repositories()
        for repository in user_repositories:
            sync_github_repository(
                repository_id=repository.repository_id, github_client=github_client, **sync_kwargs,
            )
    elif vcs_account.vcs == enums.VersionControlService.GITLAB:
        gitlab_client = vcs_clients.GitlabClient(vcs_account)
        repositories = gitlab_client.get_user_repositories()
        for repository in repositories:
            _sync_gitlab_repository(repository=repository, vcs_account=vcs_account)
    else:
        raise exceptions.ServiceException(f"vcs {vcs_account.vcs} is not supported yet!")


def sync_github_repository(
    *,
    repository_id: int,
    github_client: vcs_clients.GitHubClient,
    sync_issues: bool = True,
    sync_programming_languages: bool = True,
    is_added: bool = True,
) -> models.Repository:
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
            is_added=is_added,
        ),
    )

    # Sync repository ownership
    if repository_data.owner.owner_type == OwnerType.ORGANIZATION:
        # Sync organization
        organization = organization_services.sync_github_organization(
            organization_name=repository_data.owner.login, github_client=github_client,
        )
        repository.organization = organization
    else:
        repository.owner = github_client.vcs_account

    # Sync issues
    if sync_issues:
        sync_github_repository_issues(
            repository=repository, github_client=github_client,
        )

    # Sync repository languages
    if sync_programming_languages:
        repository.programming_languages = github_client.get_repository_languages(
            owner_name=repository.owner_name, repository_name=repository.name
        )

    repository.save()

    return repository


def sync_github_repository_issues(*, repository: models.Repository, github_client: vcs_clients.GitHubClient) -> None:
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


def _sync_gitlab_repository(
    *,
    repository: vcs_clients.gitlab.models.Repository,
    vcs_account: users_models.VCSAccount,
    extra_defaults: dict = None,
) -> Tuple[models.Repository, bool]:
    defaults = dict(
        name=repository.name,
        description=repository.description,
        url=repository.web_url,
        stars_count=repository.star_count,
        open_issues_count=repository.open_issues_count,
        forks_count=repository.forks_count,
        created_at=repository.created_at,
        updated_at=repository.last_activity_at,
        visibility=repository.visibility,
    )

    if extra_defaults:
        defaults.update(extra_defaults)

    # Add ownership
    if repository.namespace.kind == NamespaceKind.ORGANIZATION:
        defaults["organization"], _ = organizations_models.Organization.objects.get_or_create(
            vcs=enums.VersionControlService.GITLAB,
            remote_id=repository.namespace.namespace_id,
            defaults=dict(name=repository.namespace.name),
        )
    else:
        defaults["owner"] = vcs_account

    # Sync repository data
    repository_obj, created = models.Repository.objects.update_or_create(
        vcs=enums.VersionControlService.GITLAB, remote_id=repository.repository_id, defaults=defaults,
    )

    return repository_obj, created
