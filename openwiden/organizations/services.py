import typing as t
from datetime import datetime

from openwiden import enums
from openwiden.organizations import models
from openwiden.users import models as users_models


class Organization:
    @staticmethod
    def sync(
        version_control_service: str,
        remote_id: int,
        name: str,
        description: str = None,
        url: str = None,
        avatar_url: str = None,
        created_at: datetime = None,
        visibility: str = enums.VisibilityLevel.private,
    ) -> t.Tuple[models.Organization, bool]:
        organization, created = models.Organization.objects.update_or_create(
            version_control_service=version_control_service,
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
    def sync_member(
        organization: models.Organization, user: users_models.User, is_admin: bool
    ) -> t.Tuple[models.Member, bool]:
        member, created = models.Member.objects.update_or_create(
            organization=organization, user=user, is_admin=is_admin
        )
        return member, created

    @staticmethod
    def remove_member(org: models.Organization, user: users_models.User):
        org.member_set.filter(user=user).delete()
