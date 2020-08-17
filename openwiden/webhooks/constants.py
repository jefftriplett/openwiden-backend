from enum import Enum


class IssueEventActions(str, Enum):
    OPENED = "opened"
    EDITED = "edited"
    DELETED = "deleted"
    PINNED = "pinned"
    UNPINNED = "unpinned"
    CLOSED = "closed"
    REOPENED = "reopened"
    ASSIGNED = "assigned"
    UNASSIGNED = "unassigned"
    LABELED = "labeled"
    UNLABELED = "unlabeled"
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    TRANSFERRED = "transferred"
    MILESTONED = "milestoned"
    DEMILESTONED = "demilestoned"


class GithubRepositoryAction(str, Enum):
    CREATED = "created"
    DELETED = "deleted"
    ARCHIVED = "archived"
    UNARCHIVED = "unarchived"
    EDITED = "edited"
    RENAMED = "renamed"
    TRANSFERRED = "transferred"
    PUBLICIZED = "publicized"
    PRIVATIZED = "privatized"
