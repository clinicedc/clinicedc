from edc.entry_meta_data.models import MetaDataMixin
from edc_visit_tracking.models import PreviousVisitMixin, VisitTrackingModelMixin


class TestVisitModel(MetaDataMixin, PreviousVisitMixin, VisitTrackingModelMixin):

    REQUIRES_PREVIOUS_VISIT = True

    def get_subject_identifier(self):
        return self.appointment.registered_subject.subject_identifier

    def custom_post_update_entry_meta_data(self):
        pass

    def get_requires_consent(self):
        return False

    class Meta:
        app_label = 'edc_offstudy'
