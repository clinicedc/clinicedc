from django.db import models

from edc_base.model.models import BaseUuidModel
from edc_meta_data.managers import CrfMetaDataManager
from edc_meta_data.models import CrfMetaDataMixin
from edc_visit_tracking.models import CrfModelMixin
from edc_visit_tracking.models import PreviousVisitMixin, VisitModelMixin
from edc_export.managers.export_history_manager import ExportHistoryManager
from edc_export.models.export_tracking_fields_mixin import ExportTrackingFieldsMixin


class TestVisitModel1(CrfMetaDataMixin, PreviousVisitMixin, VisitModelMixin):

    REQUIRES_PREVIOUS_VISIT = True

    def get_subject_identifier(self):
        return self.appointment.registered_subject.subject_identifier

    def get_requires_consent(self):
        return False

    class Meta:
        app_label = 'edc_export'


class TestCrfModel1(CrfModelMixin, ExportTrackingFieldsMixin, BaseUuidModel):

    test_visit_model1 = models.OneToOneField(TestVisitModel1)

    f1 = models.CharField(max_length=10, null=True)
    f2 = models.CharField(max_length=10, null=True)
    f3 = models.CharField(max_length=10, null=True)

    entry_meta_data_manager = CrfMetaDataManager(TestVisitModel1)
    export_history = ExportHistoryManager()

    def get_subject_identifier(self):
        return self.test_visit.get_subject_identifier()

    class Meta:
        app_label = 'edc_export'
