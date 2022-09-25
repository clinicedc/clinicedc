from datetime import datetime


class VisitTrackingModelFormMixin:
    report_datetime_field_attr = "report_datetime"

    @property
    def subject_identifier(self) -> str:
        return self.cleaned_data.get("subject_identifier") or self.instance.subject_identifier

    @property
    def report_datetime(self) -> datetime:
        return self.cleaned_data.get(self.report_datetime_field_attr) or getattr(
            self.instance, self.report_datetime_field_attr
        )
