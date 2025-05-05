from django.db import models

from .reference_range_collection import ReferenceRangeCollection


class ReferenceModelMixin(models.Model):

    reference_range_collection = models.ForeignKey(
        ReferenceRangeCollection, on_delete=models.PROTECT
    )

    label = models.CharField(max_length=25)

    description = models.CharField(max_length=255, null=True)

    reference_group = models.CharField(max_length=25, null=True)

    lower = models.FloatField(null=True)
    lower_operator = models.CharField(max_length=15, null=True)
    lower_inclusive = models.BooleanField(default=False)
    lln = models.CharField(default=None, max_length=15, null=True)

    upper = models.FloatField(null=True)
    upper_operator = models.CharField(max_length=2, null=True)
    upper_inclusive = models.BooleanField(default=False)
    uln = models.CharField(default=None, max_length=15, null=True)

    gender = models.CharField(max_length=15)
    units = models.CharField(max_length=15)

    age_units = models.CharField(max_length=15)

    age_lower = models.IntegerField()
    age_lower_operator = models.CharField(max_length=15)
    age_lower_inclusive = models.BooleanField(default=False)

    age_upper = models.IntegerField()
    age_upper_operator = models.CharField(max_length=15)
    age_upper_inclusive = models.BooleanField(default=False)

    fasting = models.BooleanField(default=False)

    phrase = models.CharField(max_length=50, null=True)

    age_phrase = models.CharField(max_length=25, null=True)

    grade = models.IntegerField(null=True)

    class Meta:
        abstract = True
