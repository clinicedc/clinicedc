from django.contrib import admin
from django.db import models


class TestModel(models.Model):

    f1 = models.CharField(max_length=10, null=True)

    class Meta:
        verbose_name = "Test Model"


admin.site.register(TestModel)
