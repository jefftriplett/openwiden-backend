from django.utils.translation import gettext_lazy as _


GITLAB_WEBHOOK_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S %Z"


class Headers:
    SIGNATURE = "HTTP_X_HUB_SIGNATURE"
    EVENT = "HTTP_X_GITHUB_EVENT"


class Messages:
    X_HUB_SIGNATURE_HEADER_IS_MISSING = _("HTTP_X_HUB_SIGNATURE header is missing.")
    X_GITHUB_EVENT_HEADER_IS_MISSING = _("HTTP_X_GITHUB_EVENT header is missing.")
    DIGEST_IS_NOT_SUPPORTED = _("{digest_name} is not supported digest.")
    X_HUB_SIGNATURE_IS_INVALID = _("HTTP_X_HUB_SIGNATURE header value is invalid.")
    REPO_WEBHOOK_CREATE_ERROR = _("Error occurred while repository webhook create: {error}.")
    VCS_IS_NOT_IMPLEMENTED = _("{vcs} is not implemented.")


class Events:
    ISSUES = "issues"
    PING = "ping"


class IssueEventActions:
    OPENED = "opened"
    EDITED = "edited"
    DELETED = "deleted"
    CLOSED = "closed"
