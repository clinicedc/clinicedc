from django.db import models


class BaseProfile(models.Model):

    name = models.CharField(
        verbose_name='Profile Name',
        max_length=50,
        unique=True)

    objects = models.Manager()

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True
