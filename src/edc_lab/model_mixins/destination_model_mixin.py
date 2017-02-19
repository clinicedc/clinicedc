from django.db import models


class DestinationModelMixin(models.Model):

    name = models.CharField(
        max_length=25,
        unique=True)

    description = models.CharField(
        max_length=50)

    address = models.TextField(
        verbose_name='Address',
        null=True,
        blank=True,
        max_length=250)

    tel = models.CharField(
        verbose_name='Telephone',
        null=True,
        blank=True,
        max_length=50)

    email = models.CharField(
        verbose_name='Email',
        null=True,
        blank=True,
        max_length=25)

    def __str__(self):
        return self.description

    def natural_key(self):
        return (self.name, )

    class Meta:
        abstract = True
        ordering = ('name', )
