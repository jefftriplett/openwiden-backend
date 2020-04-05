from django.test import TestCase, override_settings

from repositories.tests import factories
from repositories.models import Repository
from repositories.filters import RepositoryFilter


@override_settings(USE_TZ=False)
class RepositoryFilterTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        for i in range(1, 7):
            count = i * 5
            host = "github.com" if i <= 3 else "gitlab.com"
            date = "2018-01-01" if i <= 3 else "2019-01-01"
            factories.Repository.create(
                version_control_service__host=host,
                name=f"Test {i}",
                star_count=count,
                open_issues_count=count,
                forks_count=count,
                created_at=date,
                updated_at=date,
            )

    def test_meta(self):
        self.assertEqual(RepositoryFilter.Meta.model, Repository)
        self.assertEqual(
            RepositoryFilter.Meta.fields,
            (
                "version_control_service",
                "star_count_gte",
                "open_issues_count_gte",
                "forks_count_gte",
                "created_at",
                "updated_at",
                "programming_language",
            ),
        )

    def test_version_control_service_filter(self):
        query = {"version_control_service": "github.com"}
        f = RepositoryFilter(query, Repository.objects.all())
        self.assertEqual(f.qs.count(), 3)
        self.assertTrue(f.qs.filter(name__in=["Test 1", "Test 2", "Test 3"]).count(), 3)

    def test_star_count_gte_filter(self):
        query = {"star_count_gte": 20}
        f = RepositoryFilter(query, Repository.objects.all())
        self.assertEqual(f.qs.count(), 3)
        self.assertEqual(f.qs.filter(name__in=["Test 4", "Test 5", "Test 6"]).count(), 3)

    def test_open_issues_count_gte_filter(self):
        query = {"open_issues_count_gte": 20}
        f = RepositoryFilter(query, Repository.objects.all())
        self.assertEqual(f.qs.count(), 3)
        self.assertEqual(f.qs.filter(name__in=["Test 4", "Test 5", "Test 6"]).count(), 3)

    def test_forks_count_gte_filter(self):
        query = {"forks_count_gte": 20}
        f = RepositoryFilter(query, Repository.objects.all())
        self.assertEqual(f.qs.count(), 3)
        self.assertEqual(f.qs.filter(name__in=["Test 4", "Test 5", "Test 6"]).count(), 3)

    def test_created_at_filter(self):
        query = {"created_at_after": "2017-01-01", "created_at_before": "2018-02-01"}
        f = RepositoryFilter(query, Repository.objects.all())
        self.assertEqual(f.qs.count(), 3)
        self.assertEqual(f.qs.filter(name__in=["Test 1", "Test 2", "Test 3"]).count(), 3)

    def test_updated_at_filter(self):
        query = {"updated_at_after": "2018-02-01", "updated_at_before": "2019-02-01"}
        f = RepositoryFilter(query, Repository.objects.all())
        self.assertEqual(f.qs.count(), 3)
        self.assertEqual(f.qs.filter(name__in=["Test 4", "Test 5", "Test 6"]).count(), 3)

    def test_programming_language_filter(self):
        r = Repository.objects.first()
        r.programming_languages = {"TEST": 1}
        r.save()
        query = {"programming_language": "TEST"}
        f = RepositoryFilter(query, Repository.objects.all())
        self.assertEqual(f.qs.count(), 1)
        self.assertEqual(f.qs.first().name, r.name)
