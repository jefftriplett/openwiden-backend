from openwiden.tests.cases import ModelTestCase
from repositories.tests.factories import VersionControlServiceFactory, RepositoryFactory, IssueFactory
from django.utils.translation import gettext_lazy as _


class VersionControlServiceModelTestCase(ModelTestCase):
    factory = VersionControlServiceFactory

    def test_name_field(self):
        self.assertFieldMaxLength("name", 100)
        self.assertFieldVerboseNameEqual("name", _("name"))

    def test_host_field(self):
        self.assertFieldMaxLength("host", 50)
        self.assertFieldVerboseNameEqual("host", _("host"))

    def test_meta(self):
        self.assertEqual(self.meta.verbose_name, _("version control service"))
        self.assertEqual(self.meta.verbose_name_plural, _("version control services"))

    def test_str(self):
        self.assertTrue(str(self.instance), self.instance.name)


class RepositoryModelTestCase(ModelTestCase):
    factory = RepositoryFactory

    def test_meta(self):
        self.assertEqual(self.meta.verbose_name, _("repository"))
        self.assertEqual(self.meta.verbose_name_plural, _("repositories"))
        self.assertTrue(self.meta.constraints[0].name, "unique_repository")

    def test_str(self):
        self.assertTrue(str(self.instance), self.instance.name)


class IssueModelTestCase(ModelTestCase):
    factory = IssueFactory

    def test_meta(self):
        self.assertEqual(self.meta.verbose_name, _("issue"))
        self.assertEqual(self.meta.verbose_name_plural, _("issues"))
        self.assertTrue(self.meta.constraints[0].name, "unique_issue")

    def test_str(self):
        self.assertTrue(str(self.instance), self.instance.title)
