class Webhook:
    def __init__(
        self,
        webhook_id: int,
        url: str,
        project_id: int,
        repository_update_events: bool,
        push_events: bool,
        push_events_branch_filter: str,
        issues_events: bool,
        confidential_issues_events: bool,
        merge_requests_events: bool,
        tag_push_events: bool,
        note_events: bool,
        confidential_note_events: bool,
        job_events: bool,
        pipeline_events: bool,
        wiki_page_events: bool,
        enable_ssl_verification: bool,
        created_at: str,
        **kwargs,
    ) -> None:
        self.webhook_id = webhook_id
        self.url = url
        self.project_id = project_id
        self.repository_update_events = repository_update_events
        self.push_events = push_events
        self.push_events_branch_filter = push_events_branch_filter
        self.issues_events = issues_events
        self.confidential_issues_events = confidential_issues_events
        self.merge_requests_events = merge_requests_events
        self.tag_push_events = tag_push_events
        self.note_events = note_events
        self.confidential_note_events = confidential_note_events
        self.job_events = job_events
        self.pipeline_events = pipeline_events
        self.wiki_page_events = wiki_page_events
        self.enable_ssl_verification = enable_ssl_verification
        self.created_at = created_at

    @classmethod
    def from_json(cls, data: dict) -> "Webhook":
        data["webhook_id"] = data.pop("id")
        return Webhook(**data)
