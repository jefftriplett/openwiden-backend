import factory
from factory import fuzzy


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "users.User"
        django_get_or_create = ("login",)

    id = factory.Faker("uuid4")
    login = factory.Sequence(lambda n: f"testuser{n}")
    github_token = fuzzy.FuzzyText(length=40)
    email = factory.Faker("email")
    name = factory.Faker("first_name")
