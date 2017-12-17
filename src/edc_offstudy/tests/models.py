from django.db import models
from django.db.models.deletion import PROTECT
from edc_appointment.model_mixins import CreateAppointmentsMixin
from edc_appointment.models import Appointment
from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_utcnow
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_visit_schedule.model_mixins.enrollment_model_mixin import EnrollmentModelMixin
from edc_visit_tracking.model_mixins import VisitModelMixin
from edc_visit_tracking.model_mixins.crf_model_mixin import CrfModelMixin

from ..model_mixins import OffstudyModelMixin, OffstudyCrfModelMixin, OffstudyNonCrfModelMixin


class SubjectConsent(NonUniqueSubjectIdentifierFieldMixin,
                     UpdatesOrCreatesRegistrationModelMixin,
                     BaseUuidModel):

    identity = models.CharField(max_length=50)

    confirm_identity = models.CharField(max_length=50)

    consent_datetime = models.DateTimeField(
        default=get_utcnow)

    report_datetime = models.DateTimeField(default=get_utcnow)

    dob = models.DateField()

    @property
    def registration_unique_field(self):
        return 'subject_identifier'


class SubjectVisit(VisitModelMixin, BaseUuidModel):

    appointment = models.OneToOneField(Appointment, on_delete=PROTECT)


class CrfOne(OffstudyCrfModelMixin, CrfModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(max_length=50, null=True, blank=True)

    f2 = models.CharField(max_length=50, null=True, blank=True)

    f3 = models.CharField(max_length=50, null=True, blank=True)


class NonCrfOne(NonUniqueSubjectIdentifierFieldMixin, OffstudyNonCrfModelMixin,
                BaseUuidModel):

    report_datetime = models.DateTimeField(default=get_utcnow)

    class Meta(OffstudyNonCrfModelMixin.Meta):
        visit_schedule_name = 'visit_schedule.'


class BadNonCrfOne(NonUniqueSubjectIdentifierFieldMixin, OffstudyNonCrfModelMixin,
                   BaseUuidModel):

    report_datetime = models.DateTimeField(default=get_utcnow)

    class Meta:
        pass


class Enrollment(EnrollmentModelMixin, CreateAppointmentsMixin, BaseUuidModel):

    subject_identifier = models.CharField(max_length=50)

    report_datetime = models.DateTimeField(default=get_utcnow)

    class Meta(EnrollmentModelMixin.Meta):
        visit_schedule_name = 'visit_schedule.schedule'


class SubjectOffstudy(OffstudyModelMixin, BaseUuidModel):

    class Meta(OffstudyModelMixin.Meta):
        consent_model = 'edc_offstudy.subjectconsent'


class BadSubjectOffstudy1(OffstudyModelMixin, BaseUuidModel):

    class Meta(OffstudyModelMixin.Meta):
        consent_model = None


class BadSubjectOffstudy2(OffstudyModelMixin, BaseUuidModel):

    class Meta:
        pass
