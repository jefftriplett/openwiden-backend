import collections
import re
from typing import Optional


PATTERN = re.compile(r"(?P<protocol>https|http)://(?P<host>\w*.\w*)/(?P<owner>[\w-]*)/(?P<repo>[\w-]*)")

ParsedUrl = collections.namedtuple("ParsedUrl", ["protocol", "host", "owner", "repo"])


def parse_repo_url(url: str) -> Optional[ParsedUrl]:
    """
    Parses repo by regex or returns None if no match found.
    """
    match = re.match(PATTERN, url)

    if match:
        parsed_url = ParsedUrl(**match.groupdict())
        if parsed_url.owner and parsed_url.repo:
            return parsed_url

    return None
