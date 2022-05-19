from django.db import models
from django.db.models.deletion import PROTECT
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_list_data.model_mixins import ListModelMixin
from edc_locator.model_mixins import LocatorModelMixin
from edc_model.models import BaseUuidModel
from edc_offstudy.model_mixins import (
    OffstudyModelManager,
    OffstudyModelMixin,
    OffstudyVisitModelMixin,
)
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_utils import get_dob, get_utcnow, get_uuid
from edc_visit_schedule.model_mixins import OffScheduleModelMixin, OnScheduleModelMixin
from edc_visit_tracking.managers import VisitModelManager
from edc_visit_tracking.model_mixins import (
    SubjectVisitMissedModelMixin,
    VisitModelMixin,
)

from edc_appointment.models import Appointment


class SubjectConsent(
    NonUniqueSubjectIdentifierFieldMixin,
    UpdatesOrCreatesRegistrationModelMixin,
    BaseUuidModel,
):
    consent_datetime = models.DateTimeField(default=get_utcnow)

    report_datetime = models.DateTimeField(default=get_utcnow)

    consent_identifier = models.UUIDField(default=get_uuid)

    dob = models.DateField(default=get_dob(25))

    identity = models.CharField(max_length=36, default=get_uuid)

    confirm_identity = models.CharField(max_length=36, default=get_uuid)

    version = models.CharField(max_length=25, default="1")

    def save(self, *args, **kwargs):
        self.confirm_identity = self.identity
        super().save(*args, **kwargs)

    @property
    def registration_unique_field(self):
        return "subject_identifier"


class OnSchedule(OnScheduleModelMixin, BaseUuidModel):
    pass


class OffSchedule(OffScheduleModelMixin, BaseUuidModel):
    pass


class OnScheduleOne(OnScheduleModelMixin, BaseUuidModel):
    pass


class OffScheduleOne(OffScheduleModelMixin, BaseUuidModel):
    pass


class OnScheduleTwo(OnScheduleModelMixin, BaseUuidModel):
    pass


class OffScheduleTwo(OffScheduleModelMixin, BaseUuidModel):
    pass


class OnScheduleThree(OnScheduleModelMixin, BaseUuidModel):
    pass


class OffScheduleThree(OffScheduleModelMixin, BaseUuidModel):
    pass


class SubjectVisitMissedReasons(ListModelMixin):
    pass


class SubjectVisit(VisitModelMixin, OffstudyVisitModelMixin, BaseUuidModel):
    appointment = models.OneToOneField(Appointment, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    comments = models.TextField(null=True)

    objects = VisitModelManager()

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Subject Visit"
        verbose_name_plural = "Subject Visit"


class SubjectVisitMissed(SubjectVisitMissedModelMixin, BaseUuidModel):

    subject_visit = models.OneToOneField(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    missed_reasons = models.ManyToManyField(
        SubjectVisitMissedReasons, blank=True, related_name="missed_reasons"
    )

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Missed Visit Report"
        verbose_name_plural = "Missed Visit Report"


class SubjectLocator(LocatorModelMixin, BaseUuidModel):
    pass


class SubjectOffstudy(OffstudyModelMixin, BaseUuidModel):
    objects = OffstudyModelManager()


class SubjectOffstudy2(OffstudyModelMixin, BaseUuidModel):
    objects = OffstudyModelManager()


class CrfOne(BaseUuidModel):

    subject_visit = models.OneToOneField(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)
