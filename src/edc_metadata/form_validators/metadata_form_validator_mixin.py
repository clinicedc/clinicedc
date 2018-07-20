from ..constants import REQUIRED
from ..models import CrfMetadata, RequisitionMetadata


class MetaDataFormValidatorMixin:

    @property
    def crf_metadata_exists(self):
        """Returns True if CRF metadata exists for this visit code.
        """
        return CrfMetadata.objects.filter(
            subject_identifier=self.instance.subject_identifier,
            visit_schedule_name=self.instance.visit_schedule_name,
            schedule_name=self.instance.schedule_name,
            visit_code=self.instance.visit_code).exists()

    @property
    def crf_metadata_required_exists(self):
        """Returns True if any required CRFs for this visit code have
        not yet been keyed.
        """
        return CrfMetadata.objects.filter(
            subject_identifier=self.instance.subject_identifier,
            visit_schedule_name=self.instance.visit_schedule_name,
            schedule_name=self.instance.schedule_name,
            visit_code=self.instance.visit_code,
            entry_status=REQUIRED).exists()

    @property
    def requisition_metadata_exists(self):
        """Returns True if requisition metadata exists for this visit code.
        """
        return RequisitionMetadata.objects.filter(
            subject_identifier=self.instance.subject_identifier,
            visit_schedule_name=self.instance.visit_schedule_name,
            schedule_name=self.instance.schedule_name,
            visit_code=self.instance.visit_code).exists()

    @property
    def requisition_metadata_required_exists(self):
        """Returns True if any required requisitions for this visit code
        have not yet been keyed.
        """
        return RequisitionMetadata.objects.filter(
            subject_identifier=self.instance.subject_identifier,
            visit_schedule_name=self.instance.visit_schedule_name,
            schedule_name=self.instance.schedule_name,
            visit_code=self.instance.visit_code,
            entry_status=REQUIRED).exists()
