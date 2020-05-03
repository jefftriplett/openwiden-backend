# from openwiden.tests.cases import ModelTestCase
# from openwiden.repositories.tests import factories
# from django.utils.translation import gettext_lazy as _
#
#
#
#
# class RepositoryModelTestCase(ModelTestCase):
#     factory = factories.Repository
#
#     def test_meta(self):
#         self.assertEqual(self.meta.verbose_name, _("repository"))
#         self.assertEqual(self.meta.verbose_name_plural, _("repositories"))
#         self.assertTrue(self.meta.constraints[0].name, "unique_repository")
#
#     def test_str(self):
#         self.assertTrue(str(self.instance), self.instance.name)
#
#
# class IssueModelTestCase(ModelTestCase):
#     factory = factories.Issue
#
#     def test_meta(self):
#         self.assertEqual(self.meta.verbose_name, _("issue"))
#         self.assertEqual(self.meta.verbose_name_plural, _("issues"))
#         self.assertTrue(self.meta.constraints[0].name, "unique_issue")
#
#     def test_str(self):
#         self.assertTrue(str(self.instance), self.instance.title)
#
