__all__ = ['SubjectVisit', 'SubjectOffstudy', 'DeathReport',
           'Enrollment', 'EnrollmentTwo', 'EnrollmentThree',
           'Disenrollment', 'DisenrollmentTwo', 'DisenrollmentThree']

from django.db import models
from edc_appointment.model_mixins import CreateAppointmentsMixin
from edc_base.model_mixins import BaseUuidModel

from ..model_mixins import EnrollmentModelMixin, DisenrollmentModelMixin
from ..model_mixins import VisitScheduleFieldsModelMixin, VisitScheduleMethodsModelMixin


class SubjectVisit(VisitScheduleFieldsModelMixin,
                   VisitScheduleMethodsModelMixin, BaseUuidModel):

    subject_identifier = models.CharField(max_length=25, null=True)

    report_datetime = models.DateTimeField()


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


class Disenrollment(DisenrollmentModelMixin, BaseUuidModel):

    class Meta(DisenrollmentModelMixin.Meta):
        visit_schedule_name = 'visit_schedule.schedule'


class EnrollmentThree(EnrollmentModelMixin, CreateAppointmentsMixin, BaseUuidModel):

    class Meta(EnrollmentModelMixin.Meta):
        visit_schedule_name = 'visit_schedule.schedule_three'


class DisenrollmentThree(DisenrollmentModelMixin, BaseUuidModel):

    class Meta(DisenrollmentModelMixin.Meta):
        visit_schedule_name = 'visit_schedule.schedule_three'


# visit_schedule_two

class EnrollmentTwo(EnrollmentModelMixin, CreateAppointmentsMixin, BaseUuidModel):

    class Meta(EnrollmentModelMixin.Meta):
        visit_schedule_name = 'visit_schedule_two.schedule_two'


class DisenrollmentTwo(DisenrollmentModelMixin, BaseUuidModel):

    class Meta(DisenrollmentModelMixin.Meta):
        visit_schedule_name = 'visit_schedule_two.schedule_two'


class EnrollmentFour(EnrollmentModelMixin, CreateAppointmentsMixin, BaseUuidModel):

    class Meta(EnrollmentModelMixin.Meta):
        visit_schedule_name = 'visit_schedule_two.schedule_four'


class DisenrollmentFour(DisenrollmentModelMixin, BaseUuidModel):

    class Meta(DisenrollmentModelMixin.Meta):
        visit_schedule_name = 'visit_schedule_two.schedule_four'


class BadMetaModel(EnrollmentModelMixin, BaseUuidModel):

    class Meta(DisenrollmentModelMixin.Meta):
        visit_schedule_name = 'bad.dog'
