from enum import Enum
from typing import List, Optional


class WebhookType(str, Enum):
    REPOSITORY = "Repository"


class ContentType(str, Enum):
    JSON = "json"
    FORM = "form"


class InsecureSSL(Enum):
    VERIFICATION_IS_PERFORMED = 0
    VERIFICATION_IS_NOT_PERFORMED = 1


class LastResponse:
    def __init__(
        self,
        status: str,
        code: Optional[int] = None,
        message: Optional[str] = None
    ) -> None:
        self.status = status
        self.code = code
        self.message = message


class Config:
    def __init__(
        self,
        url: str,
        content_type: ContentType = ContentType.JSON,
        secret: str = None,
        insecure_ssl: InsecureSSL = InsecureSSL.VERIFICATION_IS_PERFORMED,
    ) -> None:
        self.url = url
        self.content_type = content_type
        self.secret = secret
        self.insecure_ssl = insecure_ssl


class Webhook:
    def __init__(
        self,
        webhook_type: WebhookType,
        webhook_id: int,
        name: str,
        active: bool,
        events: List[str],
        config: Config,
        updated_at: str,
        created_at: str,
        url: str,
        test_url: str,
        ping_url: str,
        last_response: LastResponse,
    ) -> None:
        self.webhook_type = webhook_type
        self.webhook_id = webhook_id
        self.name = name
        self.active = active
        self.events = events
        self.config = config
        self.updated_at = updated_at
        self.created_at = created_at
        self.url = url
        self.test_url = test_url
        self.ping_url = ping_url
        self.last_response = last_response

    @classmethod
    def from_json(cls, json: dict) -> "Webhook":
        config = Config(**json.pop("config"))
        last_response = LastResponse(**json.pop("last_response"))
        json["webhook_type"] = json.pop("type")
        json["webhook_id"] = json.pop("id")
        return cls(**json, config=config, last_response=last_response)
