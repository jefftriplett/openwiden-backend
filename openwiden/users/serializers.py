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


class OAuth2TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = VCSAccount
        fields = (
            "provider",
            "login",
        )


class UserWithOAuthTokensSerializer(UserSerializer):
    oauth2_tokens = OAuth2TokenSerializer(many=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ("oauth2_tokens",)
