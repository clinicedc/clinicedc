from django.db import models


class AliquotStatusModelMixin(models.Model):

    packed = models.BooleanField(default=False)

    packed_datetime = models.DateTimeField(null=True)

    shipped = models.BooleanField(default=False)

    shipped_datetime = models.DateTimeField(null=True)

    class Meta:
        abstract = True
