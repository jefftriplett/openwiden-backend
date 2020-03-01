from rest_framework import authentication


class GitHubOAuth(authentication.BaseAuthentication):
    def authenticate(self, request):
        pass
