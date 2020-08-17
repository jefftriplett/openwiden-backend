import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.functional
@pytest.mark.django_db
def test_run(create_api_client, create_repository):
    # Create api client and repository
    api_client = create_api_client()
    python_repository_languages = {"Python": 60, "Docker": 5, "JavaScript": 35}
    vue_repository_languages = {"Docker": 5, "JavaScript": 35, "Vue": 60}
    create_repository(programming_languages=python_repository_languages)
    create_repository(programming_languages=vue_repository_languages)

    # Make request
    response = api_client.get(reverse("api-v1:repositories:programming_languages"))

    # Test
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == sorted(
        set(list(python_repository_languages.keys()) + list(vue_repository_languages.keys()))
    )

    # TODO: send filter request with a language
    ...
