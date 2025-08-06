from edc_constants.constants import CLOSED
from edc_form_validators import INVALID_ERROR

from edc_protocol_incident.constants import WITHDRAWN


class IncidentFormvalidatorMixin:
    def validate_close_report(self):
        self.required_if(
            CLOSED,
            WITHDRAWN,
            field="report_status",
            field_required="corrective_action_datetime",
        )
        self.required_if(
            CLOSED, WITHDRAWN, field="report_status", field_required="corrective_action"
        )
        self.required_if(
            CLOSED,
            WITHDRAWN,
            field="report_status",
            field_required="preventative_action_datetime",
        )
        self.required_if(
            CLOSED, WITHDRAWN, field="report_status", field_required="preventative_action"
        )
        self.required_if(
            CLOSED, WITHDRAWN, field="report_status", field_required="action_required"
        )
        self.required_if(
            CLOSED, WITHDRAWN, field="report_status", field_required="report_closed_datetime"
        )
        self.required_if(WITHDRAWN, field="report_status", field_required="reasons_withdrawn")

        self.validate_date_not_before_incident("report_closed_datetime")

    def validate_date_not_before_incident(self, fld_name):
        if self.cleaned_data.get(fld_name) and self.cleaned_data.get("incident_datetime"):
            if self.cleaned_data.get(fld_name) < self.cleaned_data.get("incident_datetime"):
                self.raise_validation_error(
                    {fld_name: "May not be before incident date/time"},
                    error_code=INVALID_ERROR,
                )
