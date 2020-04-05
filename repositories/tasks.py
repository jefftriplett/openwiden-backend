import requests
from github import Github
from gitlab import Gitlab
from django.conf import settings
from django.utils.timezone import make_aware
from django.core.mail import send_mail
from django_q.tasks import async_task

from repositories import models
from repositories.utils import ParsedUrl


github = Github(client_id=settings.GITHUB_CLIENT_ID, client_secret=settings.GITHUB_SECRET_KEY)
gitlab = Gitlab("https://gitlab.com", private_token=settings.GITLAB_PRIVATE_TOKEN)


def add_github_repository(user, parsed_url: ParsedUrl, service: "models.VersionControlService"):
    repo = github.get_repo(f"{parsed_url.owner}/{parsed_url.repo}")

    # Check if repository already exists
    qs = models.Repository.objects.filter(version_control_service=service, remote_id=repo.id)
    if qs.exists():
        async_task(add_repository_send_email, "exists", user)
    # Check if repo is private
    elif repo.private:
        async_task(add_repository_send_email, "private", user)
    # Add repo then
    else:
        # Get repo issues
        # issues_data = repo.get_issues(state="open")
        # issues = [
        #     dict(
        #         remote_id=i.id,
        #         title=i.title,
        #         description=i.body,
        #         state=i.state,
        #         labels=[label.name for label in i.labels],
        #         url=i.html_url,
        #         created_at=make_aware(i.created_at),
        #         updated_at=make_aware(i.updated_at),
        #     )
        #     for i in issues_data
        #     if not i.pull_request  # exclude pull requests
        # ]

        programming_languages = repo.get_languages()
        main_pl_name = max(programming_languages, key=lambda k: programming_languages[k])
        pl, created = models.ProgrammingLanguage.objects.get_or_create(name=main_pl_name)

        if created:
            # TODO: notify on new pl add
            pass

        # Create repository with nested data
        repository = models.Repository.new(
            version_control_service=service,
            remote_id=repo.id,
            name=repo.name,
            description=repo.description,
            url=repo.html_url,
            forks_count=repo.forks_count,
            star_count=repo.stargazers_count,
            created_at=make_aware(repo.created_at),
            updated_at=make_aware(repo.updated_at),
            programming_language=pl,
            # issues=issues,
        )

        async_task(add_repository_send_email, "added", user, repository)


def add_gitlab_repository(user, parsed_url: ParsedUrl, service: "models.VersionControlService"):
    repo_raw = requests.get(f"https://gitlab.com/api/v4/projects/{parsed_url.owner}%2F{parsed_url.repo}").json()
    repo = gitlab.projects.get(id=repo_raw["id"])

    # Check if repository already exists
    qs = models.Repository.objects.filter(version_control_service=service, remote_id=repo.id)
    if qs.exists():
        async_task(add_repository_send_email, "exists", user)
    else:
        # Get repo issues
        # issues_data = repo.issues.list(state="opened")
        # issues = [
        #     dict(
        #         remote_id=i.id,
        #         title=i.title,
        #         description=i.description,
        #         state="open",
        #         labels=i.labels,
        #         url=i.web_url,
        #         created_at=i.created_at,
        #         updated_at=i.updated_at,
        #     )
        #     for i in issues_data
        # ]

        programming_languages = repo.languages()
        main_pl_name = max(programming_languages, key=lambda k: programming_languages[k])
        pl, created = models.ProgrammingLanguage.objects.get_or_create(name=main_pl_name)

        if created:
            # TODO: notify on new pl add
            pass

        # Create repository with nested data
        repository = models.Repository.new(
            version_control_service=service,
            remote_id=repo.id,
            name=repo.name,
            description=repo.description,
            url=repo.web_url,
            forks_count=repo.forks_count,
            star_count=repo.star_count,
            created_at=repo.created_at,
            updated_at=repo.last_activity_at,
            programming_language=pl,
        )

        async_task(add_repository_send_email, "added", user, repository)


def add_repository_send_email(result, user, repository: "models.Repository" = None):
    if result == "exists":
        send_mail("Repository add request", "exists", "info@openwiden.com", [user.email])
    elif result == "private":
        send_mail("Repository add request", "private", "info@openwiden.com", [user.email])
    elif result == "added":
        send_mail("Repository add request", f"{repository.name} was added!", "info@openwiden.com", [user.email])
    else:
        raise ValueError(f"Unknown result of type '{result}'")
