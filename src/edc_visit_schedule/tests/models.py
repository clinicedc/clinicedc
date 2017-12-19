from django.db import models
from edc_appointment.model_mixins import CreateAppointmentsMixin
from edc_base.model_mixins import BaseUuidModel
from uuid import uuid4

from ..model_mixins import EnrollmentModelMixin, DisenrollmentModelMixin
from ..model_mixins import VisitScheduleFieldsModelMixin, VisitScheduleMethodsModelMixin
from edc_base.utils import get_utcnow


class SubjectVisit(VisitScheduleFieldsModelMixin,
                   VisitScheduleMethodsModelMixin, BaseUuidModel):

    subject_identifier = models.CharField(max_length=25, null=True)

    report_datetime = models.DateTimeField()

    reason = models.CharField(max_length=25, null=True)


class SubjectConsent(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25)

    consent_identifier = models.UUIDField(default=uuid4)

    report_datetime = models.DateTimeField(default=get_utcnow)

    version = models.CharField(max_length=25, default='1')


class SubjectOffstudy(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25, null=True)

    report_datetime = models.DateTimeField()


class DeathReport(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25, null=True)

    report_datetime = models.DateTimeField()


# visit_schedule

class Enrollment(EnrollmentModelMixin, CreateAppointmentsMixin, BaseUuidModel):

    class Meta(EnrollmentModelMixin.Meta):
        visit_schedule_name = 'visit_schedule.schedule'
        consent_model = 'edc_visit_schedule.subjectconsent'


class Disenrollment(DisenrollmentModelMixin, BaseUuidModel):

    class Meta(DisenrollmentModelMixin.Meta):
        visit_schedule_name = 'visit_schedule.schedule'
        consent_model = 'edc_visit_schedule.subjectconsent'


class EnrollmentThree(EnrollmentModelMixin, CreateAppointmentsMixin, BaseUuidModel):

    class Meta(EnrollmentModelMixin.Meta):
        visit_schedule_name = 'visit_schedule.schedule_three'
        consent_model = 'edc_visit_schedule.subjectconsent'


class DisenrollmentThree(DisenrollmentModelMixin, BaseUuidModel):

    class Meta(DisenrollmentModelMixin.Meta):
        visit_schedule_name = 'visit_schedule.schedule_three'
        consent_model = 'edc_visit_schedule.subjectconsent'


# visit_schedule_two

class EnrollmentTwo(EnrollmentModelMixin, CreateAppointmentsMixin, BaseUuidModel):

    class Meta(EnrollmentModelMixin.Meta):
        visit_schedule_name = 'visit_schedule_two.schedule_two'
        consent_model = 'edc_visit_schedule.subjectconsent'


class DisenrollmentTwo(DisenrollmentModelMixin, BaseUuidModel):

    class Meta(DisenrollmentModelMixin.Meta):
        visit_schedule_name = 'visit_schedule_two.schedule_two'
        consent_model = 'edc_visit_schedule.subjectconsent'


class EnrollmentFour(EnrollmentModelMixin, CreateAppointmentsMixin, BaseUuidModel):

    class Meta(EnrollmentModelMixin.Meta):
        visit_schedule_name = 'visit_schedule_two.schedule_four'
        consent_model = 'edc_visit_schedule.subjectconsent'


class DisenrollmentFour(DisenrollmentModelMixin, BaseUuidModel):

    class Meta(DisenrollmentModelMixin.Meta):
        visit_schedule_name = 'visit_schedule_two.schedule_four'
        consent_model = 'edc_visit_schedule.subjectconsent'


class BadMetaModel(EnrollmentModelMixin, BaseUuidModel):

    class Meta(DisenrollmentModelMixin.Meta):
        visit_schedule_name = 'bad.dog'
        consent_model = 'edc_visit_schedule.subjectconsent'
