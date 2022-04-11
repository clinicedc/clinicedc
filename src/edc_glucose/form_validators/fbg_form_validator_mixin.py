from edc_form_validators import FormValidator


class FbgFormValidatorMixin:
    """Declare with FormValidatorMixin"""

    def validate_fbg_required_fields(
        self: FormValidator, fbg_prefix: str, report_datetime_fld: str
    ):
        """Uses fields `fbg_value`, `fbg_datetime`, `fbg_units`.

        Args:
            :param fbg_prefix: e.g. fbg, fbg2, etc
            :param report_datetime_fld:
        """

        self.invalid_if_before_report_datetime(
            f"{fbg_prefix}_datetime", report_datetime_field=report_datetime_fld
        )
        self.required_if_true(
            self.cleaned_data.get(f"{fbg_prefix}_datetime"),
            field_required=f"{fbg_prefix}_value",
        )

        self.required_if_true(
            self.cleaned_data.get(f"{fbg_prefix}_value"),
            field_required=f"{fbg_prefix}_units",
        )

        self.required_if_true(
            self.cleaned_data.get(f"{fbg_prefix}_value"),
            field_required=f"{fbg_prefix}_datetime",
        )
