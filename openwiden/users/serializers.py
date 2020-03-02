from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
        )
        read_only_fields = ("username",)


class GitHubOAuthCodeSerializer(serializers.Serializer):
    code = serializers.CharField()


class CreateUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ("username", "first_name", "last_name", "github_token")
