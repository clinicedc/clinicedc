from django.db import models

from edc.base.model.validators import datetime_not_before_study_start, datetime_not_future

from .base_registered_subject_model import BaseRegisteredSubjectModel


class BaseRegistrationModel (BaseRegisteredSubjectModel):

    registration_datetime = models.DateTimeField(
        "Today's date",
        validators=[
            datetime_not_before_study_start,
            datetime_not_future, ])

    def get_registration_datetime(self):
        return self.registration_datetime

    def get_report_datetime(self):
        return self.registration_datetime

    class Meta:
        abstract = True
