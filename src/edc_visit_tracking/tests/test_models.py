from edc_meta_data.models import CrfMetaDataMixin
from edc_visit_tracking.models import PreviousVisitMixin, VisitModelMixin


class TestVisitModel(CrfMetaDataMixin, PreviousVisitMixin, VisitModelMixin):

    REQUIRES_PREVIOUS_VISIT = True

    def get_subject_identifier(self):
        return self.appointment.registered_subject.subject_identifier

    def custom_post_update_crf_meta_data(self):
        pass

    def get_requires_consent(self):
        return False

    class Meta:
        app_label = 'edc_visit_tracking'
