from django.contrib import admin

from repositories import models


class DisabledAddModelAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False


@admin.register(models.VersionControlService)
class VersionControlServiceAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Repository)
class RepositoryAdmin(DisabledAddModelAdmin):
    pass


@admin.register(models.Issue)
class IssueAdmin(DisabledAddModelAdmin):
    pass
