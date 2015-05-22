import dateutil.parser
from datetime import timedelta
from django.db import models
from edc_registration.models import RegisteredSubject


class BaseLocatorManager(models.Manager):

    def get_by_natural_key(self, report_datetime, subject_identifier_as_pk):
        if isinstance(report_datetime, str):
            report_datetime = dateutil.parser.parse(report_datetime)
        margin = timedelta(microseconds=999)
        registered_subject = RegisteredSubject.objects.get(subject_identifier_as_pk=subject_identifier_as_pk)
        return self.get(
            report_datetime__range=(report_datetime - margin, report_datetime + margin),
            registered_subject=registered_subject)
