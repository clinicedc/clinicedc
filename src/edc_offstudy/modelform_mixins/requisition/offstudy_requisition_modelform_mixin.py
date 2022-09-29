from ..crf import OffstudyCrfModelFormMixin


class OffstudyRequisitionModelFormMixin(OffstudyCrfModelFormMixin):

    """ModelForm mixin for Requisition Models."""

    report_datetime_field_attr = "requisition_datetime"
