# django imports
from django.db import models
from django.utils.translation import gettext_lazy as _


# USER RELATED ENUMS
class UserStatus(models.IntegerChoices):
    ACTIVE = 1, _('Active')
    INACTIVE = 2, _('Inactive')
    PENDING_INVITATION = 3, _('Pending Invitation')
    SOFT_DELETED = 4, _('Soft Deleted')


class UserRole(models.IntegerChoices):
    SUPER_ADMIN = 1, _('Super admin')
    ADMIN = 2, _('Admin')
    USER = 3, _('Customer')
    CLIENT_ADMIN = 4, _('Client admin')


class UserType(models.IntegerChoices):
    ADMIN = 1, _('Admin')
    USER = 2, _('Customer')

