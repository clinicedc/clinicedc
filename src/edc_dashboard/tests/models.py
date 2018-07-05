from django.db import models
from edc_base.model_mixins import BaseUuidModel
from edc_base.sites.site_model_mixin import SiteModelMixin
from edc_search.model_mixins import SearchSlugModelMixin, SearchSlugManager


class SubjectVisit(SiteModelMixin,
                   SearchSlugModelMixin, BaseUuidModel):

    subject_identifier = models.CharField(max_length=25, null=True)

    report_datetime = models.DateTimeField()

    reason = models.CharField(max_length=25, null=True)

    objects = SearchSlugManager()

    def get_search_slug_fields(self):
        fields = ['subject_identifier', 'reason']
        return fields


class TestModel(models.Model):

    f1 = models.CharField(
        max_length=25,
        null=True)

    class Meta:
        ordering = ('f1', )
