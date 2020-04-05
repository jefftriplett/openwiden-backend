import factory
from django.utils.timezone import now
from factory import fuzzy

from repositories import models


class ProgrammingLanguage(factory.DjangoModelFactory):
    name = fuzzy.FuzzyChoice(["Python", "C++", "C", "Go", "PHP", "Ruby", "C#", "Java", "JavaScript", "Perl"])

    class Meta:
        model = models.ProgrammingLanguage
        django_get_or_create = ("name",)


class VersionControlService(factory.DjangoModelFactory):
    name = factory.Faker("text", max_nb_chars=100)
    host = factory.Iterator(["github.com", "gitlab.com"])

    class Meta:
        model = models.VersionControlService
        django_get_or_create = ("host",)


class Repository(factory.DjangoModelFactory):
    version_control_service = factory.SubFactory(VersionControlService)
    remote_id = fuzzy.FuzzyInteger(1, 10000000)
    name = factory.Faker("text", max_nb_chars=255)
    description = factory.Faker("text")
    url = factory.Faker("url")
    forks_count = fuzzy.FuzzyInteger(1, 1000)
    star_count = fuzzy.FuzzyInteger(1, 90000)
    created_at = fuzzy.FuzzyDateTime(now())
    updated_at = fuzzy.FuzzyDateTime(now())
    open_issues_count = fuzzy.FuzzyInteger(1, 1000)
    programming_language = factory.SubFactory(ProgrammingLanguage)

    class Meta:
        model = models.Repository
        django_get_or_create = ("version_control_service", "remote_id")


class Issue(factory.DjangoModelFactory):
    repository = factory.SubFactory(Repository)
    remote_id = fuzzy.FuzzyInteger(1, 10000000)
    title = factory.Faker("text")
    description = factory.Faker("text")
    state = fuzzy.FuzzyChoice(models.Issue.STATE_CHOICES)
    labels = ["bug", "back-end"]
    url = factory.Faker("url")
    created_at = fuzzy.FuzzyDateTime(now())
    closed_at = fuzzy.FuzzyDateTime(now())
    updated_at = fuzzy.FuzzyDateTime(now())

    class Meta:
        model = models.Issue
        django_get_or_create = ("repository", "remote_id")
