from edc_form_validators import FormValidator

from ..form_validator_mixins import DeathReportFormValidatorMixin


class DeathReportFormValidator(DeathReportFormValidatorMixin, FormValidator):
    death_report_date_field = "death_datetime"
