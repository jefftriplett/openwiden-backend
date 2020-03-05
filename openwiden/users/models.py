import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    login = models.CharField(max_length=255, unique=True, verbose_name=_("login"))
    name = models.CharField(max_length=255, verbose_name=_("name"))
    email = models.EmailField(verbose_name=_("e-mail"))
    github_token = models.CharField(max_length=40, verbose_name=_("GitHub token"))

    USERNAME_FIELD = "login"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.login

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
