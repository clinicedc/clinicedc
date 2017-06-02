from django.db import models

from ..model_mixins import SearchSlugModelMixin


class TestModel(SearchSlugModelMixin, models.Model):

    search_slug_fields = ['f1', 'f2', 'f3']

    f1 = models.CharField(max_length=25, null=True)

    f2 = models.DateTimeField(null=True)

    f3 = models.IntegerField(null=True)
