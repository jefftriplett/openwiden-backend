# import requests
# import typing as t
# from github import Github, RateLimitExceededException
# from github.Repository import Repository as GitHubRepository
# from gitlab import Gitlab
# from gitlab.v4.objects import Project as GitlabRepository
# from django.conf import settings
# from django.utils.timezone import make_aware
# from django.core.mail import send_mail
# from django_q.tasks import async_task
#
# from openwiden.repositories import models, utils
# from .constants import GitProviderHost
#
#
# PAGINATION_LIMIT = 30
# github = Github(client_id=settings.GITHUB_CLIENT_ID, client_secret=settings.GITHUB_SECRET_KEY)
# gitlab = Gitlab("https://gitlab.com", private_token=settings.GITLAB_PRIVATE_TOKEN, per_page=PAGINATION_LIMIT)
#
#
# def add_repository_send_email(result, user, repository: "models.Repository" = None):
#     if result == "updated":
#         send_mail("Repository add request", "already exists", "info@openwiden.com", [user.email])
#     elif result == "rate_limit_exceeded":
#         send_mail(
#             "Repository add request",
#             "Rate limit exceeded, sorry, try again later",
#             "info@openwiden.com",
#             [user.email]
#         )
#     elif result == "added":
#         send_mail("Repository add request", f"{repository.name} was added!", "info@openwiden.com", [user.email])
#     else:
#         raise ValueError(f"Unknown result of type '{result}'")
#
#
# # TODO: create class with strategies
# def update_or_create_repository(user, service: "models.VersionControlService", owner: str, repo_name: str):
#     """
#     Task for adding a repository.
#     """
#
#     if service.host == GitProviderHost.GITHUB:
#         try:
#             repo: "GitHubRepository" = github.get_repo(f"{owner}/{repo_name}")
#         except RateLimitExceededException:
#             async_task(add_repository_send_email, "rate_limit_exceeded", user)
#             return f"Rate limit exceeded for {owner}/{repo_name} add request."
#
#         # Get programming languages
#         programming_languages = repo.get_languages()
#
#         # Set default repository values
#         kwargs = dict(
#             url=repo.html_url,
#             star_count=repo.stargazers_count,
#             created_at=make_aware(repo.created_at),
#             updated_at=make_aware(repo.updated_at),
#         )
#     elif service.host == GitProviderHost.GITLAB:
#         repo_raw = requests.get(f"https://gitlab.com/api/v4/projects/{owner}%2F{repo_name}").json()
#         repo: "GitlabRepository" = gitlab.projects.get(id=repo_raw["id"])
#         programming_languages = repo.languages()
#
#         # Set default repository values
#         kwargs = dict(
#             url=repo.web_url,
#             star_count=repo.star_count,
#             created_at=repo.created_at,
#             updated_at=repo.last_activity_at,
#         )
#     else:
#         raise NotImplementedError(f"{service} is not implemented!")
#
#     # Get or create programming language for main language
#     main_pl_name = max(programming_languages, key=lambda k: programming_languages[k])
#     pl, created = models.ProgrammingLanguage.objects.get_or_create(name=main_pl_name)
#
#     if created:
#         # TODO: notify admin for a new added language
#         pass
#
#     repository, created = models.Repository.objects.update_or_create(
#         version_control_service=service,
#         programming_language=pl,
#         remote_id=repo.id,
#         name=repo.name,
#         description=repo.description,
#         forks_count=repo.forks_count,
#         open_issues_count=repo.open_issues_count,
#         **kwargs,
#     )
#
#     # Check if repository created or just updated
#     if not created:
#         async_task(add_repository_send_email, "updated", user, repository)
#         return f"{repository.name} already exists (id: {repository.id})"
#     else:
#         # Create schedule task for issues events
#         pass
#
#     # Notify user for successfully repository add
#     async_task(add_repository_send_email, "added", user, repository)
#
#     # Download issues
#     if repo.open_issues_count > 0:
#         async_task(update_or_create_issues, repo, repository)
#
#     return f"{repository.name} was added (id: {repository.id})"
#
#
# def update_or_create_issues(repo, repository: "models.Repository"):
#     """
#     Add repository issues.
#     """
#     if repository.version_control_service.host == GitProviderHost.GITHUB:
#         issues_data = repo.get_issues(state="open")[:PAGINATION_LIMIT]
#         issues: t.List[dict] = utils.parse_github_issues(issues_data)
#     elif repository.version_control_service.host == GitProviderHost.GITLAB:
#         issues_data = repo.issues.list(state="opened", page=1)
#         issues: t.List[dict] = utils.parse_gitlab_issues(issues_data)
#     else:
#         raise NotImplementedError(f"{repository.version_control_service} is not implemented for issues download!")
#
#     # Create issues for repository
#     for i in issues:
#         models.Issue.objects.update_or_create(repository=repository, **i)
#
#     # Return successfully message
#     return f"Issues created successfully for repository {repository}: {len(issues)}"
