import pytest

from openwiden.repositories import models, filters
from openwiden import enums

pytestmark = pytest.mark.django_db


class TestRepositoryFilter:
    def test_vcs_filter(self, create_repository):
        expected = create_repository(vcs=enums.VersionControlService.GITHUB)
        create_repository(vcs=enums.VersionControlService.GITLAB)
        query = {"vcs": enums.VersionControlService.GITHUB}

        f = filters.Repository(query, models.Repository.objects.all())

        assert f.qs.count() == 1
        assert f.qs.first().id == expected.id

    def test_stars_count_gte_filter(self, create_repository):
        expected = create_repository(stars_count=20)
        create_repository(stars_count=19)
        query = {"stars_count_gte": 20}

        f = filters.Repository(query, models.Repository.objects.all())

        assert f.qs.count() == 1
        assert f.qs.first().id == expected.id

    def test_open_issues_count_gte_filter(self, create_repository):
        expected = create_repository(open_issues_count=21)
        create_repository(open_issues_count=19)
        query = {"open_issues_count_gte": 20}

        f = filters.Repository(query, models.Repository.objects.all())

        assert f.qs.count() == 1
        assert f.qs.first().id == expected.id

    def test_forks_count_gte_filter(self, create_repository):
        expected = create_repository(forks_count=21)
        create_repository(forks_count=19)
        query = {"forks_count_gte": 20}

        f = filters.Repository(query, models.Repository.objects.all())

        assert f.qs.count() == 1
        assert f.qs.first().id == expected.id

    def test_created_at_filter(self, create_repository):
        expected = create_repository(created_at="2020-05-01")
        create_repository(created_at="2010-01-01")
        query = {"created_at_after": "2017-01-01", "created_at_before": "2020-06-01"}

        f = filters.Repository(query, models.Repository.objects.all())

        assert f.qs.count() == 1
        assert f.qs.first().id == expected.id

    def test_updated_at_filter(self, create_repository):
        expected = create_repository(updated_at="2020-05-01")
        query = {"updated_at_after": "2018-02-01", "updated_at_before": "2020-06-01"}

        f = filters.Repository(query, models.Repository.objects.all())

        assert f.qs.count() == 1
        assert f.qs.first().id == expected.id
