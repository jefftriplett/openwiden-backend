import pytest

from . import factories
from openwiden.repositories import models


@pytest.fixture
def create_repository():
    def factory(**kwargs) -> models.Repository:
        return factories.Repository(**kwargs)

    return factory
