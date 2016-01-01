from django.db import models
from django.utils import timezone

from edc_appointment.models import AppointmentMixin
from edc_base.model.models.base_uuid_model import BaseUuidModel
from edc_meta_data.managers import CrfMetaDataManager
from edc_registration.models import RegisteredSubject
from edc_testing.models import TestVisit, TestPanel, TestAliquotType
from edc_visit_tracking.models.crf_model_mixin import CrfModelMixin
from edc_meta_data.managers.requisition_meta_data_manager import RequisitionMetaDataManager


class TestEnroll(AppointmentMixin, BaseUuidModel):

    registered_subject = models.ForeignKey(RegisteredSubject)
    f1 = models.CharField(max_length=10, null=True)

    def get_registration_datetime(self):
        return self.consent_datetime

    class Meta:
        app_label = 'edc_appointment'


class TestCrfModel1(CrfModelMixin, BaseUuidModel):

    test_visit = models.OneToOneField(TestVisit)

    f1 = models.CharField(max_length=10, null=True)
    f2 = models.CharField(max_length=10, null=True)
    f3 = models.CharField(max_length=10, null=True)

    objects = models.Manager()

    entry_meta_data_manager = CrfMetaDataManager(TestVisit)

    def get_subject_identifier(self):
        return self.test_visit.get_subject_identifier()

    class Meta:
        app_label = 'edc_appointment'


class TestCrfModel2(CrfModelMixin, BaseUuidModel):

    test_visit = models.OneToOneField(TestVisit)

    f1 = models.CharField(max_length=10, null=True)
    f2 = models.CharField(max_length=10, null=True)
    f3 = models.CharField(max_length=10, null=True)

    objects = models.Manager()

    entry_meta_data_manager = CrfMetaDataManager(TestVisit)

    def get_subject_identifier(self):
        return self.test_visit.get_subject_identifier()

    class Meta:
        app_label = 'edc_appointment'


class TestCrfModel3(CrfModelMixin, BaseUuidModel):

    test_visit = models.OneToOneField(TestVisit)

    f1 = models.CharField(max_length=10, null=True)
    f2 = models.CharField(max_length=10, null=True)
    f3 = models.CharField(max_length=10, null=True)

    objects = models.Manager()

    entry_meta_data_manager = CrfMetaDataManager(TestVisit)

    def get_subject_identifier(self):
        return self.test_visit.get_subject_identifier()

    class Meta:
        app_label = 'edc_appointment'


class TestRequisitionModel(BaseUuidModel):

    test_visit = models.ForeignKey(TestVisit)
    report_datetime = models.DateTimeField(default=timezone.now())
    panel = models.ForeignKey(TestPanel)
    aliquot_type = models.ForeignKey(TestAliquotType)
    site = models.CharField(max_length=10, null=True)

    objects = models.Manager()

    entry_meta_data_manager = RequisitionMetaDataManager(TestVisit)

    def get_subject_identifier(self):
        return self.test_visit.get_subject_identifier()

    class Meta:
        app_label = 'edc_appointment'
