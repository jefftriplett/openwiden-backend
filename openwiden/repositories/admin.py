from django.contrib import admin

from openwiden.repositories import models


class DisabledAddModelAdmin(admin.ModelAdmin):
    """
    Disables the creation of a model in the admin panel.
    """

    def has_add_permission(self, request):
        return False


class IssueInline(admin.TabularInline):
    model = models.Issue


@admin.register(models.Repository)
class RepositoryAdmin(DisabledAddModelAdmin):
    inlines = (IssueInline,)
