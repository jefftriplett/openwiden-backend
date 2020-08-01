class Organization:
    def __init__(
        self,
        organization_id: int,
        name: str,
        description: str,
        web_url: str,
        avatar_url: str,
        created_at: str,
        **kwargs,
    ) -> None:
        self.organization_id = organization_id
        self.name = name
        self.description = description
        self.web_url = web_url
        self.avatar_url = avatar_url
        self.created_at = created_at

    @classmethod
    def from_json(cls, data: dict) -> "Organization":
        data["organization_id"] = data.pop("id")
        return cls(**data)
