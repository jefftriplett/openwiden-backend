from typing import Tuple

from openwiden import enums, exceptions, vcs_clients
from openwiden.repositories import models, error_messages
from openwiden.users import models as users_models, selectors as users_selectors
from openwiden.organizations import models as organizations_models
from openwiden.organizations import services as organizations_services
from openwiden.vcs_clients.github.models import OwnerType
from openwiden.vcs_clients.gitlab.models.repository import NamespaceKind
from openwiden.webhooks import services as webhooks_services


def _add_github_repository(*, repository: models.Repository, vcs_account: users_models.VCSAccount,) -> None:
    github_client = vcs_clients.GitHubClient(vcs_account)

    # Sync repository
    repository_data = github_client.get_repository(repository.remote_id)
    programming_languages = github_client.get_repository_languages(repository.remote_id)
    repository, _ = sync_github_repository(
        repository=repository_data,
        vcs_account=vcs_account,
        extra_defaults=dict(is_added=True, programming_languages=programming_languages),
    )

    # Sync organization if owner is organization
    if repository.organization:
        organization_data = github_client.get_organization(repository.organization.remote_id,)
        organization, _ = organizations_services.sync_github_organization(organization=organization_data,)

        # Sync membership
        membership_type = github_client.check_organization_membership(organization_id=organization.remote_id,)
        organizations_services.sync_organization_membership(
            organization=organization, vcs_account=vcs_account, membership_type=membership_type,
        )

    # Sync issues
    repository_issues = github_client.get_repository_issues(repository.remote_id)
    for issue in repository_issues:
        sync_github_repository_issue(issue=issue, repository=repository)

    # Create webhook
    webhooks_services.create_repository_webhook(
        repository=repository, vcs_account=vcs_account,
    )


def _add_gitlab_repository(*, repository: models.Repository, vcs_account: users_models.VCSAccount,) -> None:
    gitlab_client = vcs_clients.GitlabClient(vcs_account)

    # Sync repository
    repository_data = gitlab_client.get_repository(repository_id=repository.remote_id)
    programming_languages = gitlab_client.get_repository_programming_languages(repository.remote_id)
    repository, _ = sync_gitlab_repository(
        repository=repository_data,
        vcs_account=vcs_account,
        extra_defaults=dict(is_added=True, programming_languages=programming_languages),
    )

    # Sync organization if owner is organization
    if repository.organization:
        organization_data = gitlab_client.get_organization(repository.organization.remote_id,)
        organization, _ = organizations_services.sync_gitlab_organization(organization=organization_data,)

        # Sync organization membership
        membership_type = gitlab_client.check_organization_membership(organization_id=organization.remote_id,)
        organizations_services.sync_organization_membership(
            organization=organization, vcs_account=vcs_account, membership_type=membership_type,
        )

    # Sync issues
    issues = gitlab_client.get_repository_issues(repository.remote_id)
    for issue in issues:
        sync_gitlab_repository_issue(issue=issue, repository=repository)

    # Create webhook
    webhooks_services.create_repository_webhook(
        repository=repository, vcs_account=vcs_account,
    )


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

    if vcs_account.vcs == enums.VersionControlService.GITHUB:
        _add_github_repository(repository=repository, vcs_account=vcs_account)
    elif vcs_account.vcs == enums.VersionControlService.GITLAB:
        _add_gitlab_repository(repository=repository, vcs_account=vcs_account)


def delete_issue_by_remote_id(*, vcs: str, remote_id: str) -> None:
    """
    Finds and deletes repository issue by id.
    """
    models.Issue.objects.filter(repository__vcs=vcs, remote_id=remote_id).delete()


def delete_repository_by_remote_id(*, vcs: str, remote_id: str) -> None:
    models.Repository.objects.filter(vcs=vcs, remote_id=remote_id).delete()


def remove_repository(*, repository: models.Repository, user: users_models.User,) -> None:
    vcs_account = users_selectors.find_vcs_account(user, repository.vcs)

    if repository.is_added is False:
        raise exceptions.ServiceException("repository already removed.")

    webhooks_services.delete_repository_webhook(
        repository=repository, vcs_account=vcs_account,
    )

    repository.is_added = False
    repository.save(update_fields=("is_added",))


def sync_user_repositories(*, vcs_account: users_models.VCSAccount) -> None:
    if vcs_account.vcs == enums.VersionControlService.GITHUB:
        github_client = vcs_clients.GitHubClient(vcs_account)
        user_repositories = github_client.get_user_repositories()
        for repository in user_repositories:
            sync_github_repository(repository=repository, vcs_account=vcs_account)
    elif vcs_account.vcs == enums.VersionControlService.GITLAB:
        gitlab_client = vcs_clients.GitlabClient(vcs_account)
        repositories = gitlab_client.get_user_repositories()
        for repository in repositories:
            sync_gitlab_repository(repository=repository, vcs_account=vcs_account)
    else:
        raise exceptions.ServiceException(f"vcs {vcs_account.vcs} is not supported yet!")


def sync_github_repository(
    *,
    repository: vcs_clients.github.models.Repository,
    vcs_account: users_models.VCSAccount = None,
    extra_defaults: dict = None,
) -> Tuple[models.Repository, bool]:
    defaults = dict(
        name=repository.name,
        description=repository.description,
        url=repository.html_url,
        stars_count=repository.stargazers_count,
        open_issues_count=repository.open_issues_count,
        forks_count=repository.forks_count,
        created_at=repository.created_at,
        updated_at=repository.updated_at,
        visibility=(enums.VisibilityLevel.public if not repository.private else enums.VisibilityLevel.private),
    )

    if extra_defaults:
        defaults.update(extra_defaults)

    if vcs_account:
        if repository.owner.owner_type == OwnerType.ORGANIZATION:
            defaults["organization"], _ = organizations_models.Organization.objects.get_or_create(
                vcs=enums.VersionControlService.GITHUB,
                remote_id=repository.owner.owner_id,
                defaults=dict(name=repository.owner.login),
            )
            organizations_models.Member.objects.get_or_create(
                organization=defaults["organization"], vcs_account=vcs_account,
            )
        else:
            defaults["owner"] = vcs_account

    repository_obj, created = models.Repository.objects.update_or_create(
        remote_id=repository.repository_id, vcs=enums.VersionControlService.GITHUB, defaults=defaults,
    )

    return repository_obj, created


def sync_github_repository_issue(
    *, issue: vcs_clients.github.models.Issue, repository: models.Repository = None,
) -> Tuple[models.Issue, bool]:
    if not repository:
        repository = models.Repository.objects.get(
            vcs=enums.VersionControlService.GITHUB, remote_id=issue.repository_id,
        )

    return models.Issue.objects.update_or_create(
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


def sync_gitlab_repository(
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
        organizations_models.Member.objects.get_or_create(
            organization=defaults["organization"], vcs_account=vcs_account,
        )
    else:
        defaults["owner"] = vcs_account

    # Sync repository data
    repository_obj, created = models.Repository.objects.update_or_create(
        vcs=enums.VersionControlService.GITLAB, remote_id=repository.repository_id, defaults=defaults,
    )

    return repository_obj, created


def sync_gitlab_repository_issue(
    *, issue: vcs_clients.gitlab.models.Issue, repository: models.Repository = None
) -> None:
    state = issue.state
    if state == "opened":
        state = "open"

    if repository is None:
        repository = models.Repository.objects.get(vcs=enums.VersionControlService.GITLAB, remote_id=issue.project_id,)

    models.Issue.objects.update_or_create(
        repository=repository,
        remote_id=issue.issue_id,
        defaults=dict(
            title=issue.title,
            description=issue.description,
            state=state,
            labels=issue.labels,
            url=issue.web_url,
            created_at=issue.created_at,
            updated_at=issue.updated_at,
            closed_at=issue.closed_at,
        ),
    )
