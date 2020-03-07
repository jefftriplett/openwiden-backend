from django.test import TestCase
from django.utils.translation import gettext_lazy as _


class ModelTestCase(TestCase):
    """
    Model test case class with additional asserts.
    """

    factory = None

    def setUp(self) -> None:
        self.user = self.factory.build()
        self.model = self.factory._meta.model
        self.meta = self.model._meta

    def get_field_attr(self, field, attr):
        """
        Returns model field attr by key.
        """
        field = self.meta.get_field(field)
        return getattr(field, attr)

    def assertFieldVerboseNameEqual(self, field: str, label: str = None):
        """
        Asserts that field verbose name equals for specified label.
        """
        verbose_name = self.get_field_attr(field, "verbose_name")
        self.assertEqual(verbose_name, label or _(field))

    def assertFieldMaxLength(self, field, length):
        """
        Asserts that field max length equals for specified length.
        """
        max_length = self.get_field_attr(field, "max_length")
        self.assertEqual(max_length, length)
