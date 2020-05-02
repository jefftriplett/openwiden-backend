from django.contrib import admin

from openwiden.repositories import models


class DisabledAddModelAdmin(admin.ModelAdmin):
    """
    Disables the creation of a model in the admin panel.
    """

    def has_add_permission(self, request):
        return False


@admin.register(models.Repository)
class RepositoryAdmin(DisabledAddModelAdmin):
    pass


@admin.register(models.Issue)
class IssueAdmin(DisabledAddModelAdmin):
    pass
