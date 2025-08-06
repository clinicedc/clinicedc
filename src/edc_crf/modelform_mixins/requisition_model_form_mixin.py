from .crf_model_form_mixin import CrfModelFormMixin


class RequisitionModelFormMixin(CrfModelFormMixin):
    report_datetime_field_attr = "requisition_datetime"
