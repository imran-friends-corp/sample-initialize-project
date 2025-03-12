# django
from django.db import models
from django.conf import settings
AUTH_USER_MODEL = settings.AUTH_USER_MODEL

# other
from autoslug import AutoSlugField



# BASE | ABSTRACT CLASSES
class BaseQueryModel(models.Model):
    """
        Provides with generic queries
    """

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def get_by_id(cls, id):
        return cls.objects.get(id=id)

    @classmethod
    def get_by_ids(cls, ids):
        return cls.objects.filter(id__in=ids)

    @classmethod
    def get_by_field(cls, field, value):
        return cls.objects.get(**{field: value})

    @classmethod
    def get_by_fields(cls, **kwargs):
        return cls.objects.get(**kwargs)

    @classmethod
    def get_all_by_field(cls, field, value):
        return cls.objects.filter(**{field: value})

    @classmethod
    def get_all_by_fields(cls, field_dict: dict):
        return cls.objects.filter(**field_dict)

    class Meta:
        abstract = True

class BaseAuditModel(BaseQueryModel):
    """
        Combination of
        - generic queries
        - audit fields
    """
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True

class BaseQueryAuditSlugModel(BaseAuditModel):
    """
        Combination of
        - generic queries
        - 3 audit fields
        - first_name, last_name, & slug
    """
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250, null=True, blank=True, default=None)
    slug = AutoSlugField(
        populate_from='first_name',
        always_update=True,
        unique=True,
        allow_unicode=True
    )

    class Meta:
        abstract = True

class PrimaryAuditModel(BaseAuditModel):
    """
        Combination of
        - generic queries
        - 4 audit fields
    """
    created_by = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_%(class)ss', null=True, blank=True)
    updated_by = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='updated_%(class)ss', null=True, blank=True)

    class Meta:
        abstract = True

class SecondaryAuditModel(BaseAuditModel):
    """
        Combination of
        - generic queries
        - 5 audit fields
    """
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_%(class)ss', null=True, blank=True)
    updated_by = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='updated_%(class)ss', null=True, blank=True)

    class Meta:
        abstract = True


class DateTimeAuditModel(models.Model):
    """
    Abstract base model that includes date and time audit fields.

    This model provides two fields for tracking the creation and last update timestamps of records in database.

    Attributes:
    - created_at (DateTimeField): The timestamp representing when the record was created. It is set automatically
      when a new record is added to the database.

    - updated_at (DateTimeField): The timestamp representing when the record was last updated. It is updated
      automatically when a record is modified.

    Usage:
    - You can inherit from this model to add timestamp fields to models that require tracking creation and update times.

    Example:
        class MyModel(DateTimeAuditModel):
            name = models.CharField(max_length=100)
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserHistoryAuditModel(models.Model):
    """
    Abstract base model that includes user history audit fields.

    This model provides fields for tracking the users responsible for creating and updating records in database.
    It also automatically populates these fields based on the current user making the changes.

    Attributes:
    - created_by (ForeignKey to settings.AUTH_USER_MODEL): A reference to the user who created the record.
      It is set to the current user when a new record is added. It can be null or blank if the user is not known.

    - updated_by (ForeignKey to settings.AUTH_USER_MODEL): A reference to the user who last updated the record.
      It is updated automatically when a record is modified. It can be null or blank if the user is not known.

    Related Fields:
    - created_by and updated_by fields have the on_delete option set to models.PROTECT.
      This means that when a user referenced in these fields is attempted to be deleted,
      the deletion will be protected and prevented if there are objects referencing the user.

    Methods:
        save(self, *args, **kwargs): Overrides the default save method to
        automatically populate the 'created_by' and 'updated_by' fields
        with the current user if available.

    Usage:
        You can inherit from this model to add user history tracking to models, which allows to keep a record of who
        created and updated each record.

    Example:
        class MyModel(UserHistoryAuditModel):
            name = models.CharField(max_length=100)
    Note:
    - Ensure that the `settings.AUTH_USER_MODEL` setting is correctly configured in project's settings
      to reference custom user model.
    """

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name="%(class)s_created")
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name="%(class)s_updated")

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        from apps.base.middleware import request_local
        request = getattr(request_local, "current_request", None)
        if request and request.user and not request.user.is_anonymous:
            if not self.created_by:
                self.created_by = request.user
            self.updated_by = request.user
        super().save(*args, **kwargs)


class BaseModel(DateTimeAuditModel, UserHistoryAuditModel):
    """
    A base abstract model class that provides common fields for all models.

    Fields:
    - created_at (DateTimeField): The date and time when the object was created.
    - updated_at (DateTimeField): The date and time when the object was last updated.
    - created_by (ForeignKey to settings.AUTH_USER_MODEL, optional): The user who created the object.
    - updated_by (ForeignKey to settings.AUTH_USER_MODEL, optional): The user who last updated the object.

    These fields are intended to be inherited by other models, allowing you to track creation and modification
    times as well as the users responsible for these actions.

    Usage:
    To use this base model, simply inherit from it in your other models. For example:

    ```python
    from django.db import models
    from myapp.models import BaseModel

    class MyModel(BaseModel):
        name = models.CharField(max_length=100)
        # Other fields specific to MyModel
    ```
    This will automatically include the `created_at`, `updated_at`, `created_by`, and `updated_by` fields
    in `MyModel`, making it easy to track the creation and modification history of objects.
    """

    class Meta:
        abstract = True


class EmailLog(DateTimeAuditModel):
    email = models.EmailField(null=True, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    city = models.TextField(null=True, blank=True)
    country = models.TextField(null=True, blank=True)
    class Meta:
        verbose_name = "EmailLog"

    def save(self, *args, **kwargs):
        self.city = self.city.lower()
        self.country = self.country.lower()
        return super(EmailLog, self).save(*args, **kwargs)

