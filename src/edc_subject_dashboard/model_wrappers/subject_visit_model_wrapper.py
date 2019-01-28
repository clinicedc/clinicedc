from django.conf import settings
from django.urls.base import reverse
from edc_model_wrapper import ModelWrapper
from edc_metadata.constants import REQUIRED, KEYED


class SubjectVisitModelWrapper(ModelWrapper):

    model = None
    next_url_attrs = ["subject_identifier", "appointment", "reason"]
    next_url_name = settings.DASHBOARD_URL_NAMES.get("subject_dashboard_url")

    @property
    def appointment(self):
        return str(self.object.appointment.id)

    @property
    def subject_identifier(self):
        return self.object.subject_identifier

    @property
    def dashboard_direct_href(self):
        return reverse(
            self.next_url_name,
            kwargs=dict(
                subject_identifier=self.object.subject_identifier,
                appointment=str(self.object.appointment.pk),
            ),
        )

    @property
    def crf_metadata(self):
        from edc_metadata.models import CrfMetadata

        return CrfMetadata.objects.filter(
            subject_identifier=self.object.subject_identifier,
            visit_code=self.object.visit_code,
            visit_code_sequence=self.object.visit_code_sequence,
            entry_status__in=[KEYED, REQUIRED],
        )

    @property
    def requisition_metadata(self):
        from edc_metadata.models import RequisitionMetadata

        return RequisitionMetadata.objects.filter(
            subject_identifier=self.object.subject_identifier,
            visit_code=self.object.visit_code,
            visit_code_sequence=self.object.visit_code_sequence,
            entry_status__in=[KEYED, REQUIRED],
        )
