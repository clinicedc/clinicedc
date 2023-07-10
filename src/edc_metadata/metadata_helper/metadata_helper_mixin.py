from typing import Any, List, Union

from ..constants import KEYED, REQUIRED
from ..utils import get_crf_metadata_model_cls, get_requisition_metadata_model_cls


class MetadataHelperMixin:
    """A mixin class to help with common queries against
    CRF and Requisition metadata.

    Always assumes the attr `metadata_helper_instance_attr` is set
    and refers to the model instance.
    """

    metadata_helper_instance_attr = "instance"

    @property
    def metadata_helper_instance(self) -> Any:
        if self.metadata_helper_instance_attr:
            return getattr(self, self.metadata_helper_instance_attr)
        else:
            return self

    @property
    def crf_metadata_exists(self: Any) -> bool:
        """Returns True if CRF metadata exists for this visit code."""
        return (
            get_crf_metadata_model_cls()
            .objects.filter(
                subject_identifier=self.metadata_helper_instance.subject_identifier,
                visit_schedule_name=self.metadata_helper_instance.visit_schedule_name,
                schedule_name=self.metadata_helper_instance.schedule_name,
                visit_code=self.metadata_helper_instance.visit_code,
                visit_code_sequence=self.metadata_helper_instance.visit_code_sequence,
            )
            .exists()
        )

    @property
    def crf_metadata_required_exists(self: Any) -> bool:
        """Returns True if any required CRFs for this visit code have
        not yet been keyed.
        """
        return self.get_crf_metadata_by(REQUIRED).exists()

    @property
    def crf_metadata_keyed_exists(self: Any) -> bool:
        """Returns True if any required CRFs for this visit code have
        been keyed.
        """
        return self.get_crf_metadata_by(KEYED).exists()

    def get_crf_metadata(self) -> Any:
        """Returns a queryset of crf metedata"""
        opts = dict(
            subject_identifier=self.metadata_helper_instance.subject_identifier,
            visit_schedule_name=self.metadata_helper_instance.visit_schedule_name,
            schedule_name=self.metadata_helper_instance.schedule_name,
            visit_code=self.metadata_helper_instance.visit_code,
            visit_code_sequence=self.metadata_helper_instance.visit_code_sequence,
        )
        return get_crf_metadata_model_cls().objects.filter(**opts)

    def get_crf_metadata_by(self, entry_status: Union[str, List[str]]) -> Any:
        if isinstance(entry_status, (list,)):
            opts = dict(entry_status__in=entry_status)
        else:
            opts = dict(entry_status=entry_status)
        return self.get_crf_metadata().filter(**opts)

    def get_requisition_metadata(self):
        """Returns a queryset of requisition metadata"""
        return get_requisition_metadata_model_cls().objects.filter(
            subject_identifier=self.metadata_helper_instance.subject_identifier,
            visit_schedule_name=self.metadata_helper_instance.visit_schedule_name,
            schedule_name=self.metadata_helper_instance.schedule_name,
            visit_code=self.metadata_helper_instance.visit_code,
            visit_code_sequence=self.metadata_helper_instance.visit_code_sequence,
        )

    @property
    def requisition_metadata_exists(self: Any) -> bool:
        """Returns True if requisition metadata exists for this visit code."""
        return self.get_requisition_metadata().exists()

    @property
    def requisition_metadata_required_exists(self: Any) -> bool:
        """Returns True if any required requisitions for this visit code
        have not yet been keyed.
        """
        return self.get_requisition_metadata_by(REQUIRED).exists()

    @property
    def requisition_metadata_keyed_exists(self: Any) -> bool:
        """Returns True if any required requisitions for this visit code
        have been keyed.
        """
        return self.get_requisition_metadata_by(KEYED)

    def get_requisition_metadata_by(self, entry_status: Union[str, List[str]]) -> Any:
        if isinstance(entry_status, (list,)):
            opts = dict(entry_status__in=entry_status)
        else:
            opts = dict(entry_status=entry_status)
        return self.get_requisition_metadata().filter(**opts)
