from ..constants import REQUIRED
from ..utils import get_crf_metadata_model_cls, get_requisition_metadata_model_cls


class MetaDataFormValidatorMixin:

    """Always assumes instance exists."""

    @property
    def crf_metadata_exists(self) -> bool:
        """Returns True if CRF metadata exists for this visit code."""
        return (
            get_crf_metadata_model_cls()
            .objects.filter(
                subject_identifier=self.instance.subject_identifier,
                visit_schedule_name=self.instance.visit_schedule_name,
                schedule_name=self.instance.schedule_name,
                visit_code=self.instance.visit_code,
                visit_code_sequence=self.instance.visit_code_sequence,
            )
            .exists()
        )

    @property
    def crf_metadata_required_exists(self) -> bool:
        """Returns True if any required CRFs for this visit code have
        not yet been keyed.
        """
        return (
            get_crf_metadata_model_cls()
            .objects.filter(
                subject_identifier=self.instance.subject_identifier,
                visit_schedule_name=self.instance.visit_schedule_name,
                schedule_name=self.instance.schedule_name,
                visit_code=self.instance.visit_code,
                visit_code_sequence=self.instance.visit_code_sequence,
                entry_status=REQUIRED,
            )
            .exists()
        )

    @property
    def requisition_metadata_exists(self) -> bool:
        """Returns True if requisition metadata exists for this visit code."""
        return (
            get_requisition_metadata_model_cls()
            .objects.filter(
                subject_identifier=self.instance.subject_identifier,
                visit_schedule_name=self.instance.visit_schedule_name,
                schedule_name=self.instance.schedule_name,
                visit_code=self.instance.visit_code,
                visit_code_sequence=self.instance.visit_code_sequence,
            )
            .exists()
        )

    @property
    def requisition_metadata_required_exists(self) -> bool:
        """Returns True if any required requisitions for this visit code
        have not yet been keyed.
        """
        return (
            get_requisition_metadata_model_cls()
            .objects.filter(
                subject_identifier=self.instance.subject_identifier,
                visit_schedule_name=self.instance.visit_schedule_name,
                schedule_name=self.instance.schedule_name,
                visit_code=self.instance.visit_code,
                visit_code_sequence=self.instance.visit_code_sequence,
                entry_status=REQUIRED,
            )
            .exists()
        )
