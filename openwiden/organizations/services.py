import typing as t
from datetime import datetime

from openwiden import enums, vcs_clients
from openwiden.organizations import models
from openwiden.users import models as users_models
from openwiden.vcs_clients.github.models import MembershipType


class Organization:
    @staticmethod
    def sync(
        vcs: str,
        remote_id: int,
        name: str,
        description: str = None,
        url: str = None,
        avatar_url: str = None,
        created_at: datetime = None,
        visibility: str = enums.VisibilityLevel.private,
    ) -> t.Tuple[models.Organization, bool]:
        """
        Synchronizes organization with specified data (create or update).
        """
        organization, created = models.Organization.objects.update_or_create(
            vcs=vcs,
            remote_id=remote_id,
            defaults=dict(
                name=name,
                description=description,
                url=url,
                avatar_url=avatar_url,
                created_at=created_at,
                visibility=visibility,
            ),
        )
        return organization, created

    @staticmethod
    def remove_member(org: models.Organization, vcs_account: users_models.VCSAccount):
        """
        Removes member from organization.
        """
        org.members.filter(vcs_account=vcs_account).delete()


class Member:
    @staticmethod
    def sync(
        organization: models.Organization, vcs_account: users_models.VCSAccount, is_admin: bool
    ) -> t.Tuple[models.Member, bool]:
        """
        Synchronizes member with specified data (create or update).
        """
        member, created = models.Member.objects.update_or_create(
            organization=organization, vcs_account=vcs_account, defaults=dict(is_admin=is_admin)
        )
        return member, created


def sync_github_organization(
    *, organization_name: str, github_client: vcs_clients.GitHubClient,
) -> models.Organization:
    organization_data = github_client.get_organization(organization_name=organization_name,)

    organization, created = models.Organization.objects.update_or_create(
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
        models.Member.objects.update_or_create(
            organization=organization, vcs_account=github_client.vcs_account, defaults=dict(is_admin=is_admin),
        )
    else:
        organization.members.filter(vcs_account=github_client.vcs_account).delete()

    return organization
