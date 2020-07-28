from django.contrib import admin

from openwiden.repositories import models
from openwiden.webhooks import admin as webhook_admin


class DisabledAddModelAdmin(admin.ModelAdmin):
    """
    Disables the creation of a model in the admin panel.
    """

    def has_add_permission(self, request):
        return False


class IssueInline(admin.StackedInline):
    model = models.Issue
    extra = 0

    def has_add_permission(self, request, obj):
        return False


@admin.register(models.Repository)
class RepositoryAdmin(DisabledAddModelAdmin):
    inlines = (IssueInline, webhook_admin.RepositoryWebhookInline)
