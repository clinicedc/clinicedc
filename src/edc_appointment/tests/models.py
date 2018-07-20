from django.db import models
from django.db.models.deletion import PROTECT
from edc_base import get_utcnow, get_dob, get_uuid
from edc_base.model_mixins import BaseUuidModel
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_locator.model_mixins import LocatorModelMixin
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_visit_schedule.model_mixins import OnScheduleModelMixin
from edc_visit_tracking.model_mixins import VisitModelMixin

from ..models import Appointment


class MyModel(VisitModelMixin, BaseUuidModel):
    pass


class SubjectConsent(NonUniqueSubjectIdentifierFieldMixin,
                     UpdatesOrCreatesRegistrationModelMixin,
                     BaseUuidModel):

    consent_datetime = models.DateTimeField(
        default=get_utcnow)

    report_datetime = models.DateTimeField(default=get_utcnow)

    consent_identifier = models.UUIDField(default=get_uuid)

    dob = models.DateField(default=get_dob(25))

    identity = models.CharField(max_length=25, default=get_uuid)

    confirm_identity = models.CharField(max_length=25, default=get_uuid)

    version = models.CharField(max_length=25, default='1')

    def save(self, *args, **kwargs):
        self.confirm_identity = self.identity
        super().save(*args, **kwargs)

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


class SubjectLocator(LocatorModelMixin, BaseUuidModel):

    pass
