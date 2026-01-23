from clinicedc_constants import NO, YES
from edc_form_validators import FormValidator


class FbgFormValidatorMixin:
    """Declare with FormValidatorMixin, modelform"""

    def validate_fbg_required_fields(self: FormValidator, fbg_prefix: str):
        """Uses fields `fbg_value`, `fbg_datetime`, `fbg_units`.

        Args:
            :param fbg_prefix: e.g. fbg, fbg2, etc
        """
        self.required_if(
            NO,
            field=f"{fbg_prefix}_performed",
            field_required=f"{fbg_prefix}_not_performed_reason",
        )

        self.required_if(
            YES,
            field=f"{fbg_prefix}_performed",
            field_required=f"{fbg_prefix}_datetime",
        )

        self.date_is_after_or_raise(
            field=f"{fbg_prefix}_datetime",
            reference_field=self.report_datetime_field_attr,
            inclusive=True,
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

        self.applicable_if_true(
            self.cleaned_data.get(f"{fbg_prefix}_value"),
            field_applicable=f"{fbg_prefix}_diagnostic_device",
        )
