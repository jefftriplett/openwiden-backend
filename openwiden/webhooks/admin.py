from django.contrib import admin

from openwiden.webhooks import models


@admin.register(models.RepositoryWebhook)
class RepositoryWebhookAdmin(admin.ModelAdmin):
    pass
