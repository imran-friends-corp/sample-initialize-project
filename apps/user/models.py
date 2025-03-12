# django imports
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# internal imports
from .enums import UserStatus, UserRole, UserType
from .managers import UserManager
from apps.common.helper import generate_unique_uuid
from apps.base.models import BaseModel


class User(BaseModel, AbstractUser):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(db_index=True, unique=False, max_length=150, null=True, blank=True)
    uuid = models.UUIDField(unique=True, max_length=150, null=False, blank=False)
    display_name = models.CharField(max_length=150, null=True, blank=True)

    status = models.PositiveSmallIntegerField(choices=UserStatus.choices, default=UserStatus.ACTIVE)
    role = models.PositiveSmallIntegerField(choices=UserRole.choices, default=UserRole.USER)
    type = models.PositiveSmallIntegerField(choices=UserType.choices, default=UserType.USER)
    note = models.CharField(max_length=150, null=True, blank=True)
    lang = models.CharField(max_length=255, choices=[('en', 'English'), ('ja', 'Japanese')], default='en')

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        if not self.uuid:
            self.uuid = generate_unique_uuid(model=self.__class__)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email if self.email else self.username}"