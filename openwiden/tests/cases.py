from django.test import TestCase
from django.utils.translation import gettext_lazy as _
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from urllib.parse import urlencode

from rest_framework_simplejwt.tokens import RefreshToken


class ModelTestCase(TestCase):
    """
    Model test case class with additional asserts.
    """

    factory = None

    def setUp(self) -> None:
        self.instance = self.factory.build()
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


class ViewTestCase(APITestCase):
    url_namespace = None

    def get_url(self, *, postfix: str = None, query: dict = None, **kwargs):
        """
        Build url for both view set or api view cases.
        """
        view_name = self.url_namespace

        # Append postfix
        if postfix:
            view_name = f"{view_name}-{postfix}"

        # Build url
        url = reverse(view_name, kwargs=kwargs)

        # Append query parameters
        if query:
            url = f"{url}?{urlencode(query)}"

        return url

    def set_auth_header(self, user):
        """
        Sets auth header for JWT auth required view.
        """
        access_token = str(RefreshToken.for_user(user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"JWT {access_token}")
