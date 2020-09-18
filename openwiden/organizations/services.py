from typing import Tuple

from openwiden import enums, vcs_clients
from openwiden.organizations import models, exceptions
from openwiden.users import models as users_models


def sync_github_organization(
    *, organization: vcs_clients.github.models.Organization,
) -> Tuple[models.Organization, bool]:
    return models.Organization.objects.update_or_create(
        vcs=enums.VersionControlService.GITHUB,
        remote_id=organization.organization_id,
        defaults=dict(
            name=organization.login,
            description=organization.description,
            url=organization.html_url,
            avatar_url=organization.avatar_url,
            created_at=organization.created_at,
        ),
    )


def sync_gitlab_organization(
    *, organization: vcs_clients.gitlab.models.Organization,
) -> Tuple[models.Organization, bool]:
    return models.Organization.objects.update_or_create(
        vcs=enums.VersionControlService.GITLAB,
        remote_id=organization.organization_id,
        defaults=dict(
            name=organization.name,
            description=organization.description,
            url=organization.web_url,
            avatar_url=organization.avatar_url,
            created_at=organization.created_at,
        ),
    )


def sync_organization_membership(
    *,
    organization: models.Organization,
    vcs_account: users_models.VCSAccount,
    membership_type: enums.OrganizationMembershipType,
) -> Tuple[models.Member, bool]:
    if membership_type == enums.OrganizationMembershipType.MEMBER:
        is_admin = False
    elif membership_type == enums.OrganizationMembershipType.ADMIN:
        is_admin = True
    else:
        raise exceptions.UserIsNotOrganizationMember()

    return models.Member.objects.update_or_create(
        organization=organization, vcs_account=vcs_account, defaults=dict(is_admin=is_admin),
    )
