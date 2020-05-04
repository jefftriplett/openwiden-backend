from django.contrib import admin
from openwiden.organizations import models


class MembersInline(admin.TabularInline):
    model = models.Member


@admin.register(models.Organization)
class Organization(admin.ModelAdmin):
    inlines = (MembersInline,)
