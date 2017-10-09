from django.db import models
from edc_base.model_mixins import BaseUuidModel

from edc_visit_schedule.model_mixins import VisitScheduleFieldsModelMixin, VisitScheduleMethodsModelMixin
from edc_search.model_mixins import SearchSlugModelMixin, SearchSlugManager


class SubjectVisit(VisitScheduleFieldsModelMixin,
                   VisitScheduleMethodsModelMixin,
                   SearchSlugModelMixin, BaseUuidModel):

    subject_identifier = models.CharField(max_length=25, null=True)

    report_datetime = models.DateTimeField()

    reason = models.CharField(max_length=25, null=True)

    objects = SearchSlugManager()

    def get_search_slug_fields(self):
        fields = ['subject_identifier', 'reason']
        return fields
