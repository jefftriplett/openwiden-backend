from enum import Enum


class OwnerType(str, Enum):
    USER = "User"
    ORGANIZATION = "Organization"


class Owner:
    def __init__(
        self,
        login: str,
        owner_id: int,
        owner_type: OwnerType,
        **kwargs
    ) -> None:
        self.login = login
        self.owner_id = owner_id
        self.owner_type = owner_type

    @classmethod
    def from_json(cls, json) -> "Owner":
        json["owner_id"] = json.pop("id")
        json["owner_type"] = json.pop("type")
        return cls(**json)
