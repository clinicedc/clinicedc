from edc_constants.constants import YES
from edc_form_validators import INVALID_ERROR, FormValidator
from edc_prn.modelform_mixins import PrnFormValidatorMixin
from edc_utils.date import to_local

from .mixins import IncidentFormvalidatorMixin


class ProtocolIncidentFormValidator(
    IncidentFormvalidatorMixin, PrnFormValidatorMixin, FormValidator
):
    def clean(self):
        self.required_if(YES, field="safety_impact", field_required="safety_impact_details")

        self.required_if(
            YES,
            field="study_outcomes_impact",
            field_required="study_outcomes_impact_details",
        )
        if (
            self.cleaned_data.get("incident_datetime")
            and self.report_datetime
            and self.cleaned_data.get("incident_datetime") > to_local(self.report_datetime)
        ):
            self.raise_validation_error(
                {"incident_datetime": "May not be after report date/time"},
                error_code=INVALID_ERROR,
            )
        self.validate_other_specify(field="incident", other_specify_field="incident_other")

        self.required_if_not_none(
            field="corrective_action_datetime", field_required="corrective_action"
        )
        self.validate_date_not_before_incident("corrective_action_datetime")
        self.required_if_not_none(
            field="preventative_action_datetime", field_required="preventative_action"
        )
        self.validate_date_not_before_incident("preventative_action_datetime")

        self.validate_close_report()
