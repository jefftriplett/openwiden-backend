import pytest

pytestmark = pytest.mark.django_db


class TestRepositoryModel:
    def test_str(self, repository):
        assert str(repository) == repository.name


class TestIssueModel:
    def test_str(self, issue):
        assert str(issue) == issue.title
