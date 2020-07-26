from .owner import Owner


class Repository:
    def __init__(
        self,
        repository_id: int,
        name: str,
        description: str,
        html_url: str,
        stargazers_count: int,
        open_issues_count: int,
        forks_count: int,
        created_at: str,
        updated_at: str,
        private: bool,
        owner: Owner,
        **kwargs
    ) -> None:
        self.repository_id = repository_id
        self.name = name
        self.description = description
        self.html_url = html_url
        self.stargazers_count = stargazers_count
        self.open_issues_count = open_issues_count
        self.forks_count = forks_count
        self.created_at = created_at
        self.updated_at = updated_at
        self.private = private
        self.owner = owner

    @classmethod
    def from_json(cls, json: dict) -> "Repository":
        json["repository_id"] = json.pop("id")
        json["owner"] = Owner.from_json(json.pop("owner"))
        return Repository(**json)
