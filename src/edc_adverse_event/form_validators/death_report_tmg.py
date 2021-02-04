from edc_constants.constants import CLOSED, NO, OTHER
from edc_form_validators import FormValidator


class DeathReportTmgFormValidator(FormValidator):
    def clean(self):

        self.required_if(
            CLOSED,
            field="report_status",
            field_required="cause_of_death",
            inverse=False,
        )

        self.validate_other_specify(
            field="cause_of_death",
            other_specify_field="cause_of_death_other",
            other_stored_value=OTHER,
        )

        self.required_if(
            CLOSED,
            field="report_status",
            field_required="cause_of_death_agreed",
            inverse=False,
        )

        self.required_if(
            NO, field="cause_of_death_agreed", field_required="narrative", inverse=False
        )

        self.required_if(
            CLOSED, field="report_status", field_required="report_closed_datetime"
        )
