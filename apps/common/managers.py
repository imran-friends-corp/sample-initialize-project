from django.db.models.signals import post_save
from django.db import models


class CustomManager(models.Manager):
    def bulk_create(self, objs, **kwargs):
        objs = super().bulk_create(objs, **kwargs)
        for obj in objs:
            post_save.send(obj.__class__, instance=obj, created=True)

        return objs
