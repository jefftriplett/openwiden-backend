from enum import Enum


class GitHubOwnerType(Enum):
    ORGANIZATION = "Organization"
    USER = "User"


class GitlabNamespaceKind(Enum):
    ORGANIZATION = "group"
    USER = "user"
