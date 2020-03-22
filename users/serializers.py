from rest_framework import serializers

from .models import User, OAuth2Token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


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
        pass
