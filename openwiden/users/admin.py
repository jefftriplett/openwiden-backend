from django.contrib import admin
from .models import User, OAuth2Token


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(OAuth2Token)
class OAuth2TokenAdmin(admin.ModelAdmin):
    pass
