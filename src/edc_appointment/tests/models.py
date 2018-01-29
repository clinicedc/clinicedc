from django.db import models
from django.db.models.deletion import PROTECT
from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_utcnow
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_visit_schedule.model_mixins import OnScheduleModelMixin
from edc_visit_tracking.model_mixins import VisitModelMixin
from uuid import uuid4

from ..models import Appointment


class MyModel(VisitModelMixin, BaseUuidModel):
    pass


class SubjectConsent(NonUniqueSubjectIdentifierFieldMixin,
                     UpdatesOrCreatesRegistrationModelMixin,
                     BaseUuidModel):

    consent_datetime = models.DateTimeField(
        default=get_utcnow)

    report_datetime = models.DateTimeField(default=get_utcnow)

    consent_identifier = models.UUIDField(default=uuid4)

    @property
    def registration_unique_field(self):
        return 'subject_identifier'


class OnScheduleOne(OnScheduleModelMixin, BaseUuidModel):

    pass


class OnScheduleTwo(OnScheduleModelMixin, BaseUuidModel):

    pass


class SubjectVisit(VisitModelMixin, BaseUuidModel):

    appointment = models.OneToOneField(Appointment, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)
