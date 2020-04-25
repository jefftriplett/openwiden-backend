from rest_framework import serializers


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
