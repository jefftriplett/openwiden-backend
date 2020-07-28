from enum import Enum


class NamespaceKind(str, Enum):
    ORGANIZATION = "group"
    USER = "user"


class Namespace:
    def __init__(self, namespace_id: int, name: str, path: str, kind: str, full_path: str, **kwargs,) -> None:
        self.namespace_id = namespace_id
        self.name = name
        self.path = path
        self.kind = kind
        self.full_path = full_path

    @classmethod
    def from_json(cls, data: dict) -> "Namespace":
        data["namespace_id"] = data.pop("id")
        return Namespace(**data)


class Repository:
    def __init__(
        self,
        repository_id: int,
        name: str,
        description: str,
        web_url: str,
        star_count: int,
        open_issues_count: int,
        forks_count: int,
        created_at: int,
        visibility: str,
        last_activity_at: int,
        namespace: Namespace,
        **kwargs,
    ) -> None:
        self.repository_id = repository_id
        self.name = name
        self.description = description
        self.web_url = web_url
        self.star_count = star_count
        self.open_issues_count = open_issues_count
        self.forks_count = forks_count
        self.created_at = created_at
        self.last_activity_at = last_activity_at
        self.visibility = visibility
        self.namespace = namespace

    @classmethod
    def from_json(cls, data: dict) -> "Repository":
        data["repository_id"] = data.pop("id")
        data["namespace"] = Namespace.from_json(data.pop("namespace"))
        return Repository(**data)
