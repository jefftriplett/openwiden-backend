from typing import List


class Issue:
    def __init__(
        self,
        issue_id: str,
        title: str,
        html_url: str,
        body: str,
        state: str,
        labels: List[str],
        created_at: str,
        updated_at: str,
        closed_at: str,
        **kwargs,
    ) -> None:
        self.issue_id = issue_id
        self.title = title
        self.html_url = html_url
        self.body = body
        self.state = state
        self.labels = labels
        self.created_at = created_at
        self.updated_at = updated_at
        self.closed_at = closed_at

    @classmethod
    def from_json(cls, json: dict) -> "Issue":
        json["issue_id"] = json.pop("id")
        json["labels"] = [label["name"] for label in json["labels"]]
        return cls(**json)
