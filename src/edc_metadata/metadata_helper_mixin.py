from typing import Any

from .constants import KEYED, REQUIRED
from .utils import get_crf_metadata_model_cls, get_requisition_metadata_model_cls


class MetaDataHelperMixin:
    """A mixin class to help with common queries against
    CRF and Requisition metadata.

    Always assumes the model instance `instance_attr` exists.
    """

    instance_attr = "instance"

    @property
    def crf_metadata_exists(self: Any) -> bool:
        """Returns True if CRF metadata exists for this visit code."""
        instance = getattr(self, self.instance_attr)
        return (
            get_crf_metadata_model_cls()
            .objects.filter(
                subject_identifier=instance.subject_identifier,
                visit_schedule_name=instance.visit_schedule_name,
                schedule_name=instance.schedule_name,
                visit_code=instance.visit_code,
                visit_code_sequence=instance.visit_code_sequence,
            )
            .exists()
        )

    @property
    def crf_metadata_required_exists(self: Any) -> bool:
        """Returns True if any required CRFs for this visit code have
        not yet been keyed.
        """
        return self.get_crf_metadata_by(REQUIRED)

    @property
    def crf_metadata_keyed_exists(self: Any) -> bool:
        """Returns True if any required CRFs for this visit code have
        been keyed.
        """
        return self.get_crf_metadata_by(KEYED)

    def get_crf_metadata_by(self: Any, entry_status: str) -> Any:
        instance = getattr(self, self.instance_attr)
        return (
            get_crf_metadata_model_cls()
            .objects.filter(
                subject_identifier=instance.subject_identifier,
                visit_schedule_name=instance.visit_schedule_name,
                schedule_name=instance.schedule_name,
                visit_code=instance.visit_code,
                visit_code_sequence=instance.visit_code_sequence,
                entry_status=entry_status,
            )
            .exists()
        )

    @property
    def requisition_metadata_exists(self: Any) -> bool:
        """Returns True if requisition metadata exists for this visit code."""
        instance = getattr(self, self.instance_attr)
        return (
            get_requisition_metadata_model_cls()
            .objects.filter(
                subject_identifier=instance.subject_identifier,
                visit_schedule_name=instance.visit_schedule_name,
                schedule_name=instance.schedule_name,
                visit_code=instance.visit_code,
                visit_code_sequence=instance.visit_code_sequence,
            )
            .exists()
        )

    @property
    def requisition_metadata_required_exists(self: Any) -> bool:
        """Returns True if any required requisitions for this visit code
        have not yet been keyed.
        """
        return self.get_requisition_metadata_by(REQUIRED)

    @property
    def requisition_metadata_keyed_exists(self: Any) -> bool:
        """Returns True if any required requisitions for this visit code
        have been keyed.
        """
        return self.get_requisition_metadata_by(KEYED)

    def get_requisition_metadata_by(self, entry_status: str) -> Any:
        instance = getattr(self, self.instance_attr)
        return (
            get_requisition_metadata_model_cls()
            .objects.filter(
                subject_identifier=instance.subject_identifier,
                visit_schedule_name=instance.visit_schedule_name,
                schedule_name=instance.schedule_name,
                visit_code=instance.visit_code,
                visit_code_sequence=instance.visit_code_sequence,
                entry_status=entry_status,
            )
            .exists()
        )
