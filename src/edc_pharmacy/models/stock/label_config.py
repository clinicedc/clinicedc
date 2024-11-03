from django.db import models


class LabelConfig(models.Model):

    name = models.CharField(max_length=25, unique=True)
    line_one = models.CharField(max_length=30, blank=True, null=True)
    line_two = models.CharField(max_length=30, blank=True, null=True)
    line_three = models.CharField(max_length=30, blank=True, null=True)
    line_four = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        verbose_name = "Stock: Label configuration"
        verbose_name_plural = "Stock: Label configurations"
