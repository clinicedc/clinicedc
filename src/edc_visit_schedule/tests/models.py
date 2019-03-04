from datetime import date
from django.db import models
from django.db.models.deletion import PROTECT
from edc_appointment.models import Appointment
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_model.models import BaseUuidModel
from edc_offstudy.model_mixins import OffstudyModelMixin, OffstudyModelManager
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_utils import get_utcnow
from edc_visit_tracking.model_mixins import CrfModelMixin, VisitModelMixin

from ..model_mixins import OffScheduleModelMixin, OnScheduleModelMixin
from ..model_mixins import SubjectScheduleCrfModelMixin


class SubjectVisit(VisitModelMixin, BaseUuidModel):

    appointment = models.OneToOneField(Appointment, on_delete=PROTECT)

    subject_identifier = models.CharField(max_length=25, null=True)

    report_datetime = models.DateTimeField()

    reason = models.CharField(max_length=25, null=True)


class SubjectConsent(
    NonUniqueSubjectIdentifierFieldMixin,
    UpdatesOrCreatesRegistrationModelMixin,
    BaseUuidModel,
):

    consent_datetime = models.DateTimeField(default=get_utcnow)

    version = models.CharField(max_length=25, default="1")

    identity = models.CharField(max_length=25)

    confirm_identity = models.CharField(max_length=25)

    dob = models.DateField(default=date(1995, 1, 1))


class SubjectOffstudy(OffstudyModelMixin, BaseUuidModel):

    objects = OffstudyModelManager()


class SubjectOffstudyFive(OffstudyModelMixin, BaseUuidModel):

    objects = OffstudyModelManager()


class SubjectOffstudySix(OffstudyModelMixin, BaseUuidModel):

    objects = OffstudyModelManager()


class SubjectOffstudySeven(OffstudyModelMixin, BaseUuidModel):

    objects = OffstudyModelManager()


class DeathReport(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25, null=True)

    report_datetime = models.DateTimeField()


# visit_schedule


class OnSchedule(OnScheduleModelMixin, BaseUuidModel):

    pass


class OffSchedule(OffScheduleModelMixin, BaseUuidModel):
    class Meta(OffScheduleModelMixin.Meta):
        pass


class OnScheduleThree(OnScheduleModelMixin, BaseUuidModel):

    pass


class OffScheduleThree(OffScheduleModelMixin, BaseUuidModel):
    class Meta(OffScheduleModelMixin.Meta):
        pass


# visit_schedule_two


class OnScheduleTwo(OnScheduleModelMixin, BaseUuidModel):

    pass


class OffScheduleTwo(OffScheduleModelMixin, BaseUuidModel):

    pass


class OnScheduleFour(OnScheduleModelMixin, BaseUuidModel):

    pass


class OffScheduleFour(OffScheduleModelMixin, BaseUuidModel):

    pass


class OnScheduleFive(OnScheduleModelMixin, BaseUuidModel):

    pass


class OffScheduleFive(OffScheduleModelMixin, BaseUuidModel):

    my_offschedule_datetime = models.DateTimeField()

    class Meta(OffScheduleModelMixin.Meta):
        offschedule_datetime_field = "my_offschedule_datetime"


class OnScheduleSix(OnScheduleModelMixin, BaseUuidModel):

    pass


class OffScheduleSix(OffScheduleModelMixin, BaseUuidModel):

    my_offschedule_date = models.DateField()

    class Meta(OffScheduleModelMixin.Meta):
        offschedule_datetime_field = "my_offschedule_date"


class BadOffSchedule1(OffScheduleModelMixin, BaseUuidModel):
    """Meta.OffScheduleModelMixin.offschedule_datetime_field
    is None"""

    my_offschedule_date = models.DateField()

    class Meta(OffScheduleModelMixin.Meta):
        offschedule_datetime_field = None


class OnScheduleSeven(OnScheduleModelMixin, BaseUuidModel):

    pass


class OffScheduleSeven(OffScheduleModelMixin, BaseUuidModel):
    """Is Missing Meta.OffScheduleModelMixin
    """

    class Meta:
        pass


class CrfOne(SubjectScheduleCrfModelMixin, CrfModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    f1 = models.CharField(max_length=50, null=True, blank=True)

    f2 = models.CharField(max_length=50, null=True, blank=True)

    f3 = models.CharField(max_length=50, null=True, blank=True)
