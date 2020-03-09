from typing import Tuple


github_url = "https://github.com/"


def parse_repo_url(url: str) -> Tuple[str, str]:
    service_label, repo_name = None, None

    if url.startswith(github_url):
        i = len(github_url)
        service_label, repo_name = "github", url[i:]

    return service_label, repo_name
