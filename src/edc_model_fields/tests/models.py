from django.db import models

from edc_constants.constants import NULL_STRING
from edc_model.models import BaseUuidModel


class TestModel(BaseUuidModel):
    f1 = models.CharField(max_length=10)
    f2 = models.CharField(max_length=10)
    f3 = models.CharField(max_length=10, default=NULL_STRING, blank=False)
    f4 = models.CharField(max_length=10, default=NULL_STRING, blank=False)
    f5 = models.CharField(max_length=10)
    f5_other = models.CharField(max_length=10, default=NULL_STRING)
