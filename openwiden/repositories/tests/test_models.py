from openwiden.tests.cases import ModelTestCase
from openwiden.repositories.tests import factories
from django.utils.translation import gettext_lazy as _


# class VersionControlServiceModelTestCase(ModelTestCase):
#     factory = factories.VersionControlService
#
#     def test_name_field(self):
#         self.assertFieldMaxLength("name", 100)
#         self.assertFieldVerboseNameEqual("name", _("name"))
#
#     def test_host_field(self):
#         self.assertFieldMaxLength("host", 50)
#         self.assertFieldVerboseNameEqual("host", _("host"))
#
#     def test_meta(self):
#         self.assertEqual(self.meta.verbose_name, _("version control service"))
#         self.assertEqual(self.meta.verbose_name_plural, _("version control services"))
#
#     def test_str(self):
#         self.assertTrue(str(self.instance), self.instance.name)


class RepositoryModelTestCase(ModelTestCase):
    factory = factories.Repository

    def test_meta(self):
        self.assertEqual(self.meta.verbose_name, _("repository"))
        self.assertEqual(self.meta.verbose_name_plural, _("repositories"))
        self.assertTrue(self.meta.constraints[0].name, "unique_repository")

    def test_str(self):
        self.assertTrue(str(self.instance), self.instance.name)


class IssueModelTestCase(ModelTestCase):
    factory = factories.Issue

    def test_meta(self):
        self.assertEqual(self.meta.verbose_name, _("issue"))
        self.assertEqual(self.meta.verbose_name_plural, _("issues"))
        self.assertTrue(self.meta.constraints[0].name, "unique_issue")

    def test_str(self):
        self.assertTrue(str(self.instance), self.instance.title)


# class ProgrammingLanguageModelTestCase(ModelTestCase):
#     factory = factories.ProgrammingLanguage
#
#     def test_meta(self):
#         self.assertEqual(self.meta.verbose_name, _("programming language"))
#         self.assertEqual(self.meta.verbose_name_plural, _("list of programming languages"))
#
#     def test_str(self):
#         pl = factories.ProgrammingLanguage()
#         self.assertEqual(str(pl), pl.name)
