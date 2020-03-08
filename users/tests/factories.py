import factory

from django.contrib.auth import get_user_model


User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    id = factory.Faker("uuid4")
    username = factory.Sequence(lambda n: f"testuser{n}")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")

    class Meta:
        model = User
        django_get_or_create = ("username",)
