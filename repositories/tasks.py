import requests
from github import Github, RateLimitExceededException
from gitlab import Gitlab
from django.conf import settings
from django.utils.timezone import make_aware
from django.core.mail import send_mail
from django_q.tasks import async_task

from repositories import models


PAGINATION_LIMIT = 30
github = Github(client_id=settings.GITHUB_CLIENT_ID, client_secret=settings.GITHUB_SECRET_KEY)
gitlab = Gitlab("https://gitlab.com", private_token=settings.GITLAB_PRIVATE_TOKEN, per_page=PAGINATION_LIMIT)


def add_repository_send_email(result, user, repository: "models.Repository" = None):
    if result == "exists":
        send_mail("Repository add request", "exists", "info@openwiden.com", [user.email])
    elif result == "rate_limit_exceeded":
        send_mail(
            "Repository add request", "Rate limit exceeded, sorry, try again later", "info@openwiden.com", [user.email]
        )
    elif result == "added":
        send_mail("Repository add request", f"{repository.name} was added!", "info@openwiden.com", [user.email])
    else:
        raise ValueError(f"Unknown result of type '{result}'")


def add_repository(user, service: "models.VersionControlService", owner: str, repo: str):
    if service.host == "github.com":
        try:
            repo = github.get_repo(f"{owner}/{repo}")
        except RateLimitExceededException:
            async_task(add_repository_send_email, "rate_limit_exceeded", user)
            return f"Rate limit exceeded for {owner}/{repo} add request."

        programming_languages = repo.get_languages()
        kwargs = dict(
            url=repo.html_url,
            star_count=repo.stargazers_count,
            created_at=make_aware(repo.created_at),
            updated_at=make_aware(repo.updated_at),
        )
    elif service.host == "gitlab.com":
        repo_raw = requests.get(f"https://gitlab.com/api/v4/projects/{owner}%2F{repo}").json()
        repo = gitlab.projects.get(id=repo_raw["id"])
        programming_languages = repo.languages()
        kwargs = dict(
            url=repo.web_url, star_count=repo.star_count, created_at=repo.created_at, updated_at=repo.last_activity_at,
        )
    else:
        raise NotImplementedError(f"{service} is not implemented!")

    # Check if repository already exists
    qs = models.Repository.objects.filter(version_control_service=service, remote_id=repo.id)
    if qs.exists():
        repository = qs.first()
        async_task(add_repository_send_email, "exists", user, repository)
        return f"{repository.name} already exists (id: {repository.id})"

    # Get or create programming language for main language
    main_pl_name = max(programming_languages, key=lambda k: programming_languages[k])
    pl, created = models.ProgrammingLanguage.objects.get_or_create(name=main_pl_name)

    if created:
        # TODO: notify admin for a new added language
        pass

    repository = models.Repository.new(
        version_control_service=service,
        programming_language=pl,
        remote_id=repo.id,
        name=repo.name,
        description=repo.description,
        forks_count=repo.forks_count,
        open_issues_count=repo.open_issues_count,
        **kwargs,
    )

    # Notify user for successfully repository add
    async_task(add_repository_send_email, "added", user, repository)

    # Download last issues
    if repo.open_issues_count > 0:
        async_task(add_issues, repo, repository)

    return f"{repository.name} was added (id: {repository.id})"


def add_issues(repo, repository: "models.Repository"):
    """
    Add repository issues from specified page.
    """
    if repository.version_control_service.host == "github.com":
        issues_data = repo.get_issues(state="open")[:PAGINATION_LIMIT]
        issues = [
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
            for i in issues_data
            if not i.pull_request  # exclude pull requests
        ]
    elif repository.version_control_service.host == "gitlab.com":
        issues_data = repo.issues.list(state="opened", page=1)
        issues = [
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
            for i in issues_data
        ]
    else:
        raise NotImplementedError(f"{repository.version_control_service} is not implemented for issues download!")

    # Create issues for repository
    repository.create_issues(issues)

    # Return successfully message
    return f"Issues created successfully for repository {repository}: {len(issues)}"
