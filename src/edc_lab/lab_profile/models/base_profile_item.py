from django.db import models


class BaseProfileItem(models.Model):

    volume = models.DecimalField(verbose_name='Volume (ml)', max_digits=10, decimal_places=1, null=True)

    count = models.IntegerField(verbose_name='aliquots to create')

    class Meta:
        abstract = True
