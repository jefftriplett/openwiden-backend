import collections
import re
import typing as t

from django.utils.timezone import make_aware
from github.Issue import Issue as GitHubIssue
from gitlab.v4.objects import ProjectIssue as GitlabIssue

PATTERN = re.compile(r"(?P<protocol>https|http)://(?P<host>\w*.\w*)/(?P<owner>[\w-]*)/(?P<repo>[\w-]*)")

ParsedUrl = collections.namedtuple("ParsedUrl", ["protocol", "host", "owner", "repo"])


def parse_repo_url(url: str) -> t.Optional[ParsedUrl]:
    """
    Parses repo by regex or returns None if no match found.
    """
    match = re.match(PATTERN, url)

    if match:
        parsed_url = ParsedUrl(**match.groupdict())
        if parsed_url.owner and parsed_url.repo:
            return parsed_url

    return None


def parse_github_issues(issues: t.List[GitHubIssue]) -> t.List[dict]:
    """
    Parses each GitHub issue into compatible with repositories.Issue model dictionary.
    """
    return [
        dict(
            remote_id=i.id,
            title=i.title,
            description=i.body,
            state=i.state,
            labels=[label.name for label in i.labels],
            url=i.html_url,
            created_at=make_aware(i.created_at),
            updated_at=make_aware(i.updated_at),
        )
        for i in issues
        if not i.pull_request  # exclude pull requests
    ]


def parse_gitlab_issues(issues: t.List[GitlabIssue]) -> t.List[dict]:
    """
    Parses each GitHub issue into compatible with repositories.Issue model dictionary.
    """
    return [
        dict(
            remote_id=i.id,
            title=i.title,
            description=i.description,
            state="open",
            labels=i.labels,
            url=i.web_url,
            created_at=i.created_at,
            updated_at=i.updated_at,
        )
        for i in issues
    ]
