from django.contrib import admin

from openwiden.webhooks import models


@admin.register(models.RepositoryWebhook)
class RepositoryWebhookAdmin(admin.ModelAdmin):
    pass


class RepositoryWebhookInline(admin.StackedInline):
    model = models.RepositoryWebhook
    extra = 0

    def has_add_permission(self, request, obj):
        return False
