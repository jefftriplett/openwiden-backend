class Profile:
    def __init__(
        self,
        id: str,
        login: str,
        name: str,
        email: str,
        avatar_url: str,
        access_token: str,
        expires_at,
        split_name: bool = True,
        token_type: str = None,
        refresh_token: str = None,
        **kwargs,
    ):
        self.id = id
        self.login = login
        self._name = name
        self.email = email
        self.first_name = None
        self.last_name = None
        self.avatar_url = avatar_url
        self.access_token = access_token
        self.token_type = token_type
        self.refresh_token = refresh_token
        self.expires_at = expires_at

        if split_name:
            self.first_name, sep, self.last_name = self._name.partition(" ")
