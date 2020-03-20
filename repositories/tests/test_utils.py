from repositories.utils import parse_repo_url


success_test_cases = (
    # GitLab
    ("https://gitlab.com/inkscape/inkscape", "inkscape", "inkscape"),
    ("https://gitlab.com/gnachman/iterm2/", "gnachman", "iterm2"),
    ("https://gitlab.com/pgjones/quart.git", "pgjones", "quart"),
    ("http://gitlab.com/gitlab-org/gitlab-runner", "gitlab-org", "gitlab-runner"),
    # GitHub
    ("https://github.com/golang/go", "golang", "go"),
    ("https://github.com/getsentry/sentry/", "getsentry", "sentry"),
    ("https://github.com/sveltejs/svelte.git", "sveltejs", "svelte"),
    ("http://github.com/psf/requests", "psf", "requests"),
)


fail_test_cases = (
    "fail_test",
    "https://github.com/",
    "http://github.com",
    "https://gitlab.com/pgjones//",
    "https://bitbucket.org/owner/repo",
)


def test_parse_repo_url_success():
    for url, expected_owner, expected_repo in success_test_cases:
        parsed_url = parse_repo_url(url)
        assert parsed_url.owner == expected_owner
        assert parsed_url.repo == expected_repo


def test_parse_repo_url_fail():
    for url in fail_test_cases:
        parsed_url = parse_repo_url(url)
        assert parsed_url is None
