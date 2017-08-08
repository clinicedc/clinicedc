from django.db import models
from django.db.models.deletion import PROTECT
from edc_appointment.model_mixins import CreateAppointmentsMixin
from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_utcnow
from edc_identifier.model_mixins import NonUniqueSubjectIdentifierFieldMixin
from edc_registration.model_mixins import UpdatesOrCreatesRegistrationModelMixin
from edc_visit_schedule.model_mixins import EnrollmentModelMixin, DisenrollmentModelMixin
from edc_appointment.models import Appointment
from edc_visit_tracking.model_mixins.visit_model_mixin import VisitModelMixin
from edc_offstudy.model_mixins import OffstudyModelMixin
from edc_metadata.model_mixins.creates import CreatesMetadataModelMixin
from edc_metadata.model_mixins.updates import UpdatesCrfMetadataModelMixin
from edc_visit_tracking.model_mixins.crf_model_mixin import CrfModelMixin
from edc_visit_tracking.model_mixins.crf_inline_model_mixin import CrfInlineModelMixin


class SubjectConsent(NonUniqueSubjectIdentifierFieldMixin,
                     UpdatesOrCreatesRegistrationModelMixin,
                     BaseUuidModel):

    consent_datetime = models.DateTimeField(
        default=get_utcnow)

    report_datetime = models.DateTimeField(default=get_utcnow)


class EnrollmentOne(EnrollmentModelMixin, CreateAppointmentsMixin, BaseUuidModel):

    class Meta(EnrollmentModelMixin.Meta):
        visit_schedule_name = 'visit_schedule1.schedule1'


class EnrollmentTwo(EnrollmentModelMixin, CreateAppointmentsMixin, BaseUuidModel):

    class Meta(EnrollmentModelMixin.Meta):
        visit_schedule_name = 'visit_schedule2.schedule2'


class Disenrollment(DisenrollmentModelMixin, BaseUuidModel):

    class Meta(DisenrollmentModelMixin.Meta):
        visit_schedule_name = 'visit_schedule.schedule'


class SubjectOffstudy(OffstudyModelMixin, BaseUuidModel):

    class Meta(OffstudyModelMixin.Meta):
        pass


class SubjectVisit(VisitModelMixin, BaseUuidModel):

    appointment = models.OneToOneField(Appointment, on_delete=PROTECT)

    subject_identifier = models.CharField(max_length=50)

    reason = models.CharField(max_length=25)


class CrfOne(CrfModelMixin, BaseUuidModel):

    subject_visit = models.ForeignKey(SubjectVisit)

    f1 = models.CharField(max_length=50, null=True)

    f2 = models.CharField(max_length=50, null=True)

    f3 = models.CharField(max_length=50, null=True)


class OtherModel(BaseUuidModel):

    f1 = models.CharField(max_length=10, default='erik')


class CrfOneInline(CrfInlineModelMixin, BaseUuidModel):

    crf_one = models.ForeignKey(CrfOne)

    other_model = models.ForeignKey(OtherModel)

    f1 = models.CharField(max_length=10, default='erik')

    class Meta(CrfInlineModelMixin.Meta):
        crf_inline_parent = 'crf_one'


class BadCrfOneInline(CrfInlineModelMixin, BaseUuidModel):
    """A model class missing _meta.crf_inline_parent.
    """

    crf_one = models.ForeignKey(CrfOne)

    other_model = models.ForeignKey(OtherModel)

    f1 = models.CharField(max_length=10, default='erik')

    class Meta:
        pass


class BadCrfOneInline2(CrfInlineModelMixin, BaseUuidModel):

    crf_one = models.ForeignKey(CrfOne)

    other_model = models.ForeignKey(OtherModel)

    f1 = models.CharField(max_length=10, default='erik')

    class Meta(CrfInlineModelMixin.Meta):
        crf_inline_parent = None
