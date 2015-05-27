import six

from dateutil import parser
from datetime import timedelta

from django.db import models

from edc_appointment.models import Appointment


class BaseVisitTrackingManager(models.Manager):

    def get_by_natural_key(self, report_datetime, visit_instance,
                           visit_definition_code, subject_identifier_as_pk):
        # deserialized date follows ECMA-262 specification
        # which has less precision than that reported by mysql
        if isinstance(report_datetime, six.string_types):
            report_datetime = parser.parse(report_datetime)
        margin = timedelta(microseconds=999)
        appointment = Appointment.objects.get_by_natural_key(
            visit_instance, visit_definition_code, subject_identifier_as_pk)
        return self.get(report_datetime__range=(report_datetime - margin,
                                                report_datetime + margin),
                        appointment=appointment)
