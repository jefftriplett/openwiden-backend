class Profile:
    def __init__(
        self,
        id: str,
        login: str,
        name: str,
        email: str,
        avatar_url: str,
        access_token: str,
        expires_at: int = None,
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

    def to_dict(self):
        return dict(
            id=self.id,
            login=self.login,
            name=self._name,
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            avatar_url=self.avatar_url,
            access_token=self.access_token,
            token_type=self.token_type,
            refresh_token=self.refresh_token,
            expires_at=self.expires_at,
        )
