from django.contrib import admin
from openwiden.users import models


class VCSAccountInline(admin.StackedInline):
    model = models.VCSAccount
    extra = 0
    readonly_fields = ("vcs", "remote_id", "login")

    def has_add_permission(self, request, obj):
        return False


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    inlines = (VCSAccountInline,)
    fields = (
        "is_active",
        "username",
        "first_name",
        "last_name",
        "email",
        "avatar",
        "date_joined",
    )
