from typing import Any


class FormValidatorTestMixin:
    consent_model = None

    def validate_demographics(self) -> None:
        pass

    def get_consent_definition_or_raise(self, *args) -> Any:
        pass

    def validate_crf_report_datetime(self):
        pass

    def validate_appt_datetime_in_window_period(self: Any, appointment, *args) -> None:
        pass

    def validate_visit_datetime_in_window_period(self: Any, *args) -> None:
        pass

    def validate_crf_datetime_in_window_period(self) -> None:
        pass

    def datetime_in_window_or_raise(self, *args):
        pass
