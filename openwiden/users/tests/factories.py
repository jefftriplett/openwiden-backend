import factory
from factory import fuzzy

from openwiden.users import models


class UserFactory(factory.django.DjangoModelFactory):
    id = factory.Faker("uuid4")
    username = factory.Sequence(lambda n: f"testuser{n}")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")

    class Meta:
        model = models.User
        django_get_or_create = ("username",)


class OAuth2TokenFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    provider = fuzzy.FuzzyChoice(models.OAuth2Token.PROVIDER_CHOICES, getter=lambda c: c[0])
    remote_id = fuzzy.FuzzyInteger(1)
    login = factory.Faker("first_name")
    token_type = factory.Faker("pystr")
    access_token = factory.Faker("pystr")
    refresh_token = factory.Faker("pystr")
    expires_at = fuzzy.FuzzyInteger(100, 36000)

    class Meta:
        model = models.OAuth2Token
        django_get_or_create = ("provider", "remote_id")
