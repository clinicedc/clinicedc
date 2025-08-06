from __future__ import annotations

from edc_crf.crf_form_validator import CrfFormValidator

from .requisition_form_validator_mixin import RequisitionFormValidatorMixin


class RequisitionFormValidator(RequisitionFormValidatorMixin, CrfFormValidator):
    """Form validator for requisitions (e.g. SubjectRequisition)"""

    report_datetime_field_attr: str = "requisition_datetime"
