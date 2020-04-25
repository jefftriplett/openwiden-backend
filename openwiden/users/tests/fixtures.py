from faker import Faker

from openwiden.users.services import models as service_models

fake = Faker()


GITHUB_PROVIDER = {
    "client_id": "GITHUB_CLIENT_ID",
    "client_secret": "GITHUB_SECRET_KEY",
    "access_token_url": "https://github.com/login/oauth/access_token",
    "access_token_params": None,
    "authorize_url": "https://github.com/login/oauth/authorize",
    "authorize_params": None,
    "api_base_url": "https://api.github.com/",
    "client_kwargs": {"scope": "user:email"},
}

GITLAB_PROVIDER = {
    "client_id": "GITHUB_CLIENT_ID",
    "client_secret": "GITHUB_SECRET_KEY",
    "access_token_url": "http://gitlab.example.com/oauth/token",
    "access_token_params": None,
    "authorize_url": "https://gitlab.example.com/oauth/authorize",
    "authorize_params": None,
    "api_base_url": "https://gitlab.example.com/api/v4/",
    "client_kwargs": None,
}


class Profile(service_models.Profile):
    def __init__(self, username: str, **kwargs):
        super().__init__(**kwargs)
        self.username = username

    def json(self):
        return {
            "id": self.id,
            "login": self.login,
            "name": self._name,
            "email": self.email,
            "avatar_url": self.avatar_url,
            "username": self.username,
        }


def create_random_profile(
    id=fake.pyint(),
    login=fake.pystr(),
    name=fake.name(),
    email=fake.email(),
    avatar_url=fake.url(),
    split_name=True,
    access_token=fake.pystr(),
    expires_at=fake.pyint(),
    token_type="bearer",
    refresh_token=fake.pystr(),
    username=fake.pystr(),
) -> Profile:
    return Profile(
        id=id,
        login=login,
        name=name,
        email=email,
        avatar_url=avatar_url,
        split_name=split_name,
        access_token=access_token,
        expires_at=expires_at,
        token_type=token_type,
        refresh_token=refresh_token,
        username=username,
    )


class EmailListMock:
    """
    Mock list for additional case, when email is not retrieved from API.
    https://developer.github.com/v3/users/emails/
    https://docs.gitlab.com/ee/api/users.html#list-emails
    """

    @staticmethod
    def json():
        return [{"email": fake.email()} for _ in range(2)]
