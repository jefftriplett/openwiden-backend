import typing as t
from datetime import datetime

from openwiden import enums
from openwiden.organizations import models
from openwiden.users import models as users_models


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
