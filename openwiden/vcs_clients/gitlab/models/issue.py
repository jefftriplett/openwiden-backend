from typing import List


class Issue:
    def __init__(
        self,
        project_id: int,
        issue_id: int,
        title: str,
        description: str,
        state: str,
        labels: List[str],
        web_url: str,
        created_at: str,
        updated_at: str,
        closed_at: str,
        **kwargs,
    ) -> None:
        self.project_id = project_id
        self.issue_id = issue_id
        self.title = title
        self.description = description
        self.state = state
        self.labels = labels
        self.web_url = web_url
        self.created_at = created_at
        self.updated_at = updated_at
        self.closed_at = closed_at

    @classmethod
    def from_json(cls, data: dict) -> "Issue":
        data["issue_id"] = data.pop("id")
        return Issue(**data)
