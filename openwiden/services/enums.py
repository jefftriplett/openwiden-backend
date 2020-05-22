from enum import Enum


class GitHubOwnerType(str, Enum):
    ORGANIZATION = "Organization"
    USER = "User"


class GitlabNamespaceKind(str, Enum):
    ORGANIZATION = "group"
    USER = "user"
