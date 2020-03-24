from rest_framework import serializers

from .models import User, OAuth2Token


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
        )


class UserUpdateSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
        )


class OAuth2TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = OAuth2Token
        fields = (
            "provider",
            "login",
        )


class UserWithOAuthTokensSerializer(UserSerializer):
    oauth2_tokens = OAuth2TokenSerializer(many=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ("oauth2_tokens",)
