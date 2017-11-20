from edc_consent.field_mixins.bw import IdentityFieldsMixin
from edc_offstudy.model_mixins import OffstudyModelMixin

from django.db import models
from edc_appointment.model_mixins.appointment_model_mixin import AppointmentModelMixin
from edc_appointment.model_mixins.create_appointments_mixin import CreateAppointmentsMixin
from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_utcnow
from edc_consent.field_mixins import (
    CitizenFieldsMixin, PersonalFieldsMixin, ReviewFieldsMixin,
    VulnerabilityFieldsMixin)
from edc_consent.model_mixins import ConsentModelMixin, RequiresConsentMixin
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierModelMixin
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_visit_schedule.model_mixins import DisenrollmentModelMixin
from edc_visit_schedule.model_mixins import EnrollmentModelMixin


class SubjectConsent(ConsentModelMixin, NonUniqueSubjectIdentifierModelMixin,
                     UpdatesOrCreatesRegistrationModelMixin,
                     IdentityFieldsMixin, ReviewFieldsMixin, PersonalFieldsMixin,
                     CitizenFieldsMixin, VulnerabilityFieldsMixin, BaseUuidModel):

    class Meta(ConsentModelMixin.Meta):
        unique_together = ['subject_identifier', 'version']


class Enrollment(EnrollmentModelMixin, CreateAppointmentsMixin, BaseUuidModel):

    class Meta(EnrollmentModelMixin.Meta):
        visit_schedule_name = 'visit_schedule1.schedule1'


class Disenrollment(DisenrollmentModelMixin, RequiresConsentMixin,
                    BaseUuidModel):

    class Meta(DisenrollmentModelMixin.Meta):
        visit_schedule_name = 'visit_schedule.schedule'
        consent_model = 'edc_offstudy.subjectconsent'


class Appointment(AppointmentModelMixin, BaseUuidModel):

    class Meta(AppointmentModelMixin.Meta):
        pass


class SubjectOffstudy(OffstudyModelMixin, BaseUuidModel):

    class Meta(OffstudyModelMixin.Meta):
        verbose_name_plural = "Subject Off-study"
        consent_model = 'edc_offstudy.subjectconsent'


class SubjectVisit(models.Model):

    subject_identifier = models.CharField(max_length=25)

    report_datetime = models.DateTimeField(default=get_utcnow)
