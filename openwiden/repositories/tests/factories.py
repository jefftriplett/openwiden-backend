import factory
from django.utils.timezone import get_current_timezone
from factory import fuzzy

from openwiden.repositories import models
from openwiden import enums

from faker import Faker

fake = Faker()


# class ProgrammingLanguage(factory.DjangoModelFactory):
#     name = fuzzy.FuzzyChoice(["Python", "C++", "C", "Go", "PHP", "Ruby", "C#", "Java", "JavaScript", "Perl"])
#
#     class Meta:
#         model = models.ProgrammingLanguage
#         django_get_or_create = ("name",)


# class VersionControlService(factory.DjangoModelFactory):
#     name = factory.Faker("text", max_nb_chars=100)
#     host = factory.Iterator(["github.com", "gitlab.com"])
#
#     class Meta:
#         model = models.VersionControlService
#         django_get_or_create = ("host",)


class Repository(factory.DjangoModelFactory):
    version_control_service = fuzzy.FuzzyChoice(enums.VersionControlService.choices, getter=lambda c: c[0])
    remote_id = fuzzy.FuzzyInteger(1, 10000000)
    name = factory.Faker("text", max_nb_chars=255)
    description = factory.Faker("text")
    url = factory.Faker("url")
    forks_count = fuzzy.FuzzyInteger(1, 1000)
    star_count = fuzzy.FuzzyInteger(1, 90000)
    created_at = factory.Faker("date_time", tzinfo=get_current_timezone())
    updated_at = factory.Faker("date_time", tzinfo=get_current_timezone())
    open_issues_count = fuzzy.FuzzyInteger(1, 1000)
    programming_languages = factory.List([fake.pystr() for _ in range(3)])

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
    created_at = factory.Faker("date_time", tzinfo=get_current_timezone())
    closed_at = factory.Faker("date_time", tzinfo=get_current_timezone())
    updated_at = factory.Faker("date_time", tzinfo=get_current_timezone())

    class Meta:
        model = models.Issue
        django_get_or_create = ("repository", "remote_id")
