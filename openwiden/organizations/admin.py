from django.contrib import admin
from openwiden.organizations import models


@admin.register(models.Organization)
class Organization(admin.ModelAdmin):
    pass
