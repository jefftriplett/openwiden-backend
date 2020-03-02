from urllib import parse

import requests
import json


class Token:
    def __init__(self, access_token, scope, token_type):
        self.access_token = access_token
        self.scope = scope
        self.token_type = token_type


class GitHubOAuthException(Exception):
    pass


class GitHubOAuth:
    GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
    GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"

    def __init__(self, client_id: str, secret_key: str, scopes: list = None):
        self.client_id: str = client_id
        self.secret_key: str = secret_key
        self.scopes = scopes

    def fetch_token(self, code: str) -> Token:
        data = {
            "client_id": self.client_id,
            "client_secret": self.secret_key,
            "code": code
        }
        response = requests.post(url=self.GITHUB_TOKEN_URL, data=data)
        data = parse.parse_qs(response.text)
        if "error" in data:
            raise GitHubOAuthException(data)
        return Token(**data)

    @property
    def authorization_url(self) -> str:
        query_dict = {"client_id": self.client_id}

        if self.scopes:
            query_dict["scope"] = " ".join(self.scopes)

        query = parse.urlencode(query_dict, quote_via=parse.quote)
        url = f"{self.GITHUB_AUTH_URL}?{query}"

        return url
