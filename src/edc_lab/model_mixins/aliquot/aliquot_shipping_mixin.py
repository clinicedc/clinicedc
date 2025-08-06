from django.db import models


class AliquotShippingMixin(models.Model):
    shipped = models.BooleanField(default=False)

    class Meta:
        abstract = True
