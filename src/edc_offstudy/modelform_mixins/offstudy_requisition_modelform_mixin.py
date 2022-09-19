from .offstudy_crf_modelform_mixin import OffstudyCrfModelFormMixin


class OffstudyRequisitionModelFormMixin(OffstudyCrfModelFormMixin):

    """ModelForm mixin for Requisition Models."""

    report_datetime_field_attr = "requisition_datetime"
