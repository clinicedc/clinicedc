from edc_constants.constants import YES
from edc_form_validators import FormValidator

from ..constants import VIOLATION
from .mixins import IncidentFormvalidatorMixin


class ProtocolDeviationViolationFormValidator(IncidentFormvalidatorMixin, FormValidator):
    def clean(self):
        self.applicable_if(VIOLATION, field="report_type", field_applicable="safety_impact")
        self.required_if(YES, field="safety_impact", field_required="safety_impact_details")
        self.applicable_if(
            VIOLATION, field="report_type", field_applicable="study_outcomes_impact"
        )
        self.required_if(
            YES, field="study_outcomes_impact", field_required="study_outcomes_impact_details"
        )

        self.required_if(VIOLATION, field="report_type", field_required="violation_datetime")

        if "violation_type" in self.cleaned_data:
            self.required_if(VIOLATION, field="report_type", field_required="violation_type")
            self.validate_other_specify(
                field="violation_type",
                other_specify_field="violation_type_other",
            )
        if "violation" in self.cleaned_data:
            self.required_if(VIOLATION, field="report_type", field_required="violation")
            self.validate_other_specify(
                field="violation",
                other_specify_field="violation_other",
            )

        self.required_if(
            VIOLATION, field="report_type", field_required="violation_description"
        )
        self.required_if(VIOLATION, field="report_type", field_required="violation_reason")

        self.validate_close_report()
