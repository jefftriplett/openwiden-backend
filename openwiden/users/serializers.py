from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "login", "name", "email", "github_token")
        read_only_fields = ("id",)


class GitHubOAuthCodeSerializer(serializers.Serializer):
    code = serializers.CharField()


class CreateUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        pass

    def create(self, validated_data):
        login = validated_data.pop("login")
        instance, created = User.objects.update_or_create(login=login, defaults=validated_data)
        return instance
