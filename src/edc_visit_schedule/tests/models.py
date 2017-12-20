from django.db import models
from edc_appointment.model_mixins import CreateAppointmentsMixin
from edc_base.model_mixins import BaseUuidModel
from uuid import uuid4

from ..model_mixins import OffScheduleModelMixin, OnScheduleModelMixin
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

class OnSchedule(OnScheduleModelMixin, CreateAppointmentsMixin, BaseUuidModel):

    class Meta(OnScheduleModelMixin.Meta):
        visit_schedule_name = 'visit_schedule.schedule'
        consent_model = 'edc_visit_schedule.subjectconsent'


class OffSchedule(OffScheduleModelMixin, BaseUuidModel):

    class Meta(OffScheduleModelMixin.Meta):
        visit_schedule_name = 'visit_schedule.schedule'
        consent_model = 'edc_visit_schedule.subjectconsent'


class OnScheduleThree(OnScheduleModelMixin, CreateAppointmentsMixin, BaseUuidModel):

    class Meta(OnScheduleModelMixin.Meta):
        visit_schedule_name = 'visit_schedule.schedule_three'
        consent_model = 'edc_visit_schedule.subjectconsent'


class OffScheduleThree(OffScheduleModelMixin, BaseUuidModel):

    class Meta(OffScheduleModelMixin.Meta):
        visit_schedule_name = 'visit_schedule.schedule_three'
        consent_model = 'edc_visit_schedule.subjectconsent'


# visit_schedule_two

class OnScheduleTwo(OnScheduleModelMixin, CreateAppointmentsMixin, BaseUuidModel):

    class Meta(OnScheduleModelMixin.Meta):
        visit_schedule_name = 'visit_schedule_two.schedule_two'
        consent_model = 'edc_visit_schedule.subjectconsent'


class OffScheduleTwo(OffScheduleModelMixin, BaseUuidModel):

    class Meta(OffScheduleModelMixin.Meta):
        visit_schedule_name = 'visit_schedule_two.schedule_two'
        consent_model = 'edc_visit_schedule.subjectconsent'


class OnScheduleFour(OnScheduleModelMixin, CreateAppointmentsMixin, BaseUuidModel):

    class Meta(OnScheduleModelMixin.Meta):
        visit_schedule_name = 'visit_schedule_two.schedule_four'
        consent_model = 'edc_visit_schedule.subjectconsent'


class OffScheduleFour(OffScheduleModelMixin, BaseUuidModel):

    class Meta(OffScheduleModelMixin.Meta):
        visit_schedule_name = 'visit_schedule_two.schedule_four'
        consent_model = 'edc_visit_schedule.subjectconsent'


class BadMetaModel(OnScheduleModelMixin, BaseUuidModel):

    class Meta(OnScheduleModelMixin.Meta):
        visit_schedule_name = 'bad.dog'
        consent_model = 'edc_visit_schedule.subjectconsent'


class BadMetaModel2(OnScheduleModelMixin, BaseUuidModel):

    class Meta(OnScheduleModelMixin.Meta):
        visit_schedule_name = None
        consent_model = 'edc_visit_schedule.subjectconsent'


class BadMetaModel3(OnScheduleModelMixin, BaseUuidModel):

    class Meta(OnScheduleModelMixin.Meta):
        visit_schedule_name = 'visit_schedule_two.schedule_four'
        consent_model = None
