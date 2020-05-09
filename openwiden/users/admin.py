from django.contrib import admin
from .models import User, VCSAccount


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(VCSAccount)
class OAuth2TokenAdmin(admin.ModelAdmin):
    pass
