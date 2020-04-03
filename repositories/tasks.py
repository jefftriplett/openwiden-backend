from github import Github
from django.conf import settings
from django.utils.timezone import make_aware
from django.core.mail import send_mail
from django_q.tasks import async_task

from repositories.models import Repository, VersionControlService
from repositories.utils import ParsedUrl


github = Github(client_id=settings.GITHUB_CLIENT_ID, client_secret=settings.GITHUB_SECRET_KEY)


def add_github_repository(user, parsed_url: ParsedUrl, service: VersionControlService):
    repo = github.get_repo(f"{parsed_url.owner}/{parsed_url.repo}")

    # Check if repository already exists
    qs = Repository.objects.filter(version_control_service=service, remote_id=repo.id)
    if qs.exists():
        async_task(add_github_repository_send_email, "exists", user)

    # Check if repo is private
    if repo.private:
        async_task(add_github_repository_send_email, "private", user)

    # Get repo issues
    issues_data = repo.get_issues(state="all")
    issues = [
        dict(
            remote_id=i.id,
            title=i.title,
            description=i.body,
            state=i.state,
            labels=[label.name for label in i.labels],
            url=i.html_url,
            created_at=make_aware(i.created_at),
            closed_at=make_aware(i.closed_at) if i.closed_at else None,
            updated_at=make_aware(i.updated_at),
        )
        for i in issues_data
        if not i.pull_request  # exclude pull requests
    ]

    programming_languages = repo.get_languages()

    # Create repository with nested data
    repository = Repository.objects.nested_create(
        version_control_service=service,
        remote_id=repo.id,
        name=repo.name,
        description=repo.description,
        url=repo.html_url,
        forks_count=repo.forks_count,
        star_count=repo.stargazers_count,
        created_at=make_aware(repo.created_at),
        updated_at=make_aware(repo.updated_at),
        programming_languages=programming_languages,
        issues=issues,
    )

    async_task(add_github_repository_send_email, "added", user, repository)


def add_github_repository_send_email(result, user, repository: Repository = None):
    if result == "exists":
        send_mail("Repository add request", "exists", "info@openwiden.com", [user.email])
    elif result == "private":
        send_mail("Repository add request", "private", "info@openwiden.com", [user.email])
    elif result == "added":
        send_mail("Repository add request", f"{repository.name} was added!", "info@openwiden.com", [user.email])
    else:
        raise ValueError(f"Unknown result of type '{result}'")
