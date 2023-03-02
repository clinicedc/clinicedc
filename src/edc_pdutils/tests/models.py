from django.db import models
from django.db.models.deletion import PROTECT
from django_crypto_fields.fields.encrypted_char_field import EncryptedCharField
from edc_appointment.models import Appointment
from edc_constants.constants import YES
from edc_list_data.model_mixins import ListModelMixin
from edc_model.models import BaseUuidModel
from edc_sites.models import SiteModelMixin
from edc_utils import get_utcnow
from edc_visit_schedule.model_mixins import OffScheduleModelMixin, OnScheduleModelMixin
from edc_visit_tracking.model_mixins import VisitModelMixin


class OnSchedule(SiteModelMixin, OnScheduleModelMixin, BaseUuidModel):
    class Meta:
        app_label = "edc_pdutils"


class OffSchedule(SiteModelMixin, OffScheduleModelMixin, BaseUuidModel):
    class Meta:
        app_label = "edc_pdutils"


class SubjectVisit(VisitModelMixin, BaseUuidModel):
    appointment = models.OneToOneField(Appointment, on_delete=models.PROTECT)

    subject_identifier = models.CharField(max_length=25)

    report_datetime = models.DateTimeField(default=get_utcnow)

    visit_code = models.CharField(max_length=25, default="T0")

    reason = models.CharField(max_length=25, null=True)

    survival_status = models.CharField(max_length=25, null=True)

    last_alive_date = models.DateTimeField(null=True)

    class Meta:
        ordering = ["report_datetime"]


class SubjectConsent(BaseUuidModel):
    subject_identifier = models.CharField(max_length=25)

    consent_datetime = models.DateTimeField(default=get_utcnow)

    dob = models.DateField(null=True)

    citizen = models.CharField(max_length=25, default=YES)

    legal_marriage = models.CharField(max_length=25, null=True)

    marriage_certificate = models.CharField(max_length=25, null=True)

    happy = models.CharField(max_length=25, choices=(("YES", "YES"), ("NO", "NO")), null=True)


class SubjectLocator(BaseUuidModel):
    subject_identifier = models.CharField(max_length=25)


class CrfModelMixin(models.Model):
    subject_visit = models.OneToOneField(SubjectVisit, on_delete=PROTECT)

    report_datetime = models.DateTimeField(null=True)

    @property
    def subject_identifier(self):
        return self.subject_visit.subject_identifier

    @property
    def visit_code(self):
        return self.subject_visit.visit_code

    @property
    def related_visit(self):
        return self.subject_visit

    class Meta:
        abstract = True


class SubjectRequisition(CrfModelMixin, BaseUuidModel):
    panel_name = models.CharField(max_length=25, default="Microtube")


class ListModel(ListModelMixin):
    pass


class Crf(CrfModelMixin, BaseUuidModel):
    char1 = models.CharField(max_length=25, null=True)

    date1 = models.DateTimeField(null=True)

    int1 = models.IntegerField(null=True)

    uuid1 = models.UUIDField(null=True)

    m2m = models.ManyToManyField(ListModel)


class CrfOne(CrfModelMixin, BaseUuidModel):
    dte = models.DateTimeField(default=get_utcnow)


class CrfTwo(CrfModelMixin, BaseUuidModel):
    dte = models.DateTimeField(default=get_utcnow)


class CrfThree(CrfModelMixin, BaseUuidModel):
    UPPERCASE = models.DateTimeField(default=get_utcnow)


class CrfInline(BaseUuidModel):
    crf_one = models.ForeignKey(CrfOne, on_delete=models.PROTECT)

    crf_two = models.ForeignKey(CrfTwo, on_delete=models.PROTECT)

    dte = models.DateTimeField(default=get_utcnow)


class CrfEncrypted(CrfModelMixin, BaseUuidModel):
    encrypted1 = EncryptedCharField(null=True)
