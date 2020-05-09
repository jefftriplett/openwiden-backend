from django.contrib import admin
from openwiden.users import models


class VCSAccountInline(admin.TabularInline):
    model = models.VCSAccount


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    inlines = (VCSAccountInline,)
