from rest_framework import serializers

from .models import User, VCSAccount


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "date_joined",
            "avatar",
        )


class UserUpdateSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = (
            "username",
            "first_name",
            "last_name",
            "avatar",
        )


class VCSAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = VCSAccount
        fields = (
            "provider",
            "login",
        )


class UserWithVCSAccountsSerializer(UserSerializer):
    vcs_accounts = VCSAccountSerializer(many=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ("vcs_accounts",)
