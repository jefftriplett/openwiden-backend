class Organization:
    def __init__(
        self,
        login: str,
        organization_id: int,
        html_url: str,
        avatar_url: str,
        description: str,
        created_at: str,
        **kwargs,
    ) -> None:
        self.login = login
        self.organization_id = organization_id
        self.html_url = html_url
        self.avatar_url = avatar_url
        self.description = description
        self.created_at = created_at

    @classmethod
    def from_json(cls, json: dict) -> "Organization":
        json["organization_id"] = json.pop("id")
        return Organization(**json)
