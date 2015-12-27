from django.db import models

from edc_visit_tracking.models import VisitTrackingModelMixin, PreviousVisitMixin, CrfModelMixin
from edc_offstudy.models import OffStudyMixin, OffStudyModelMixin
from edc_base.model.models import BaseUuidModel
from edc.entry_meta_data.models import MetaDataMixin


class TestVisitModel(OffStudyMixin, MetaDataMixin, PreviousVisitMixin, VisitTrackingModelMixin):

    off_study_model = ('edc_offstudy', 'TestOffStudyModel')
    REQUIRES_PREVIOUS_VISIT = True

    def get_subject_identifier(self):
        return self.appointment.registered_subject.subject_identifier

    def custom_post_update_entry_meta_data(self):
        pass

    def get_requires_consent(self):
        return False

    class Meta:
        app_label = 'edc_offstudy'


class TestOffStudyModel(CrfModelMixin, OffStudyModelMixin, BaseUuidModel):

    test_visit_model = models.OneToOneField(TestVisitModel)

    class Meta:
        app_label = 'edc_offstudy'


class AnotherTestVisitModel(OffStudyMixin, MetaDataMixin, PreviousVisitMixin, VisitTrackingModelMixin):

    off_study_model = TestOffStudyModel
    REQUIRES_PREVIOUS_VISIT = True

    def get_subject_identifier(self):
        return self.appointment.registered_subject.subject_identifier

    def custom_post_update_entry_meta_data(self):
        pass

    def get_requires_consent(self):
        return False

    class Meta:
        app_label = 'edc_offstudy'
