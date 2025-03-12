
from django.contrib.auth.models import UserManager as BaseUserManager


class UserManager(BaseUserManager):

    def create_user(self, username=None, email=None, password=None, **extra_fields):
        return super().create_user(
            username=username if username else email, email=email, password=password, **extra_fields)

    def create_superuser(self, username=None, email=None, password=None, **extra_fields):
        return super().create_superuser(
            username=username if username else email, email=email, password=password, **extra_fields)