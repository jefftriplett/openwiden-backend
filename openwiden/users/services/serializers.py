from rest_framework import serializers

from openwiden.users import models


class GitHubUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    login = serializers.CharField()
    name = serializers.CharField()
    email = serializers.EmailField()
    avatar_url = serializers.URLField()


class GitlabUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    login = serializers.CharField()
    name = serializers.CharField()
    email = serializers.EmailField()
    avatar_url = serializers.URLField()

    def to_internal_value(self, data):
        data["login"] = data.pop("username")
        return super().to_internal_value(data)


class OAuthTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OAuth2Token
        fields = "__all__"
