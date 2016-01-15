from edc_meta_data.models import CrfMetaDataMixin
from edc_visit_tracking.models import PreviousVisitMixin, VisitModelMixin
from edc_offstudy.models import OffStudyMixin
from edc_testing.models.test_consent import TestConsentWithMixin


class TestVisitModel(CrfMetaDataMixin, OffStudyMixin, PreviousVisitMixin, VisitModelMixin):

    REQUIRES_PREVIOUS_VISIT = True

    consent_model = TestConsentWithMixin

    off_study_model = ('edc_testing', 'TestOffStudy')

    death_report_model = ('edc_testing', 'TestDeathReport')

    def get_subject_identifier(self):
        return self.appointment.registered_subject.subject_identifier

    def get_requires_consent(self):
        return False

    class Meta:
        app_label = 'edc_visit_tracking'
