from django.db import models


class Holiday(models.Model):

    day = models.DateField(
        unique=True)

    name = models.CharField(
        max_length=25,
        null=True,
        blank=True)

    @property
    def label(self):
        return self.name

    @property
    def local_date(self):
        return self.day.strftime("%Y-%m-%d")

    def __str__(self):
        return f'{self.label} on {self.local_date}'

    class Meta:
        ordering = ['day', ]
