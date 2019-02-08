from django import forms
from edc_constants.constants import OTHER
from edc_form_validators import FormValidator
from edc_form_validators import REQUIRED_ERROR, INVALID_ERROR
from edc_metadata.models import CrfMetadata, RequisitionMetadata
from edc_metadata.constants import KEYED

from ..constants import MISSED_VISIT, UNSCHEDULED
from ..visit_sequence import VisitSequence, VisitSequenceError


class VisitFormValidator(FormValidator):

    visit_sequence_cls = VisitSequence
    validate_missed_visit_reason = True
    validate_unscheduled_visit_reason = True

    def clean(self):
        appointment = self.cleaned_data.get("appointment")
        if not appointment:
            raise forms.ValidationError(
                {"appointment": "This field is required"}, code=REQUIRED_ERROR
            )

        visit_sequence = self.visit_sequence_cls(appointment=appointment)

        try:
            visit_sequence.enforce_sequence()
        except VisitSequenceError as e:
            raise forms.ValidationError(e, code=INVALID_ERROR)

        self.validate_visit_code_sequence_and_reason()

        self.validate_required_fields()

    def validate_visit_code_sequence_and_reason(self):
        appointment = self.cleaned_data.get("appointment")
        reason = self.cleaned_data.get("reason")
        if appointment:
            if not appointment.visit_code_sequence and reason == UNSCHEDULED:
                raise forms.ValidationError(
                    {"reason": "Invalid. This is not an unscheduled visit"},
                    code=INVALID_ERROR,
                )
            if appointment.visit_code_sequence and reason != UNSCHEDULED:
                raise forms.ValidationError(
                    {"reason": "Invalid. This is an unscheduled visit"},
                    code=INVALID_ERROR,
                )
            if reason == MISSED_VISIT and self.metadata_exists_for(entry_status=KEYED):
                raise forms.ValidationError(
                    {"reason": "Invalid. Some data has already been submitted"},
                    code=INVALID_ERROR,
                )

    def validate_required_fields(self):

        if self.validate_missed_visit_reason:
            self.required_if(
                MISSED_VISIT, field="reason", field_required="reason_missed"
            )

            self.required_if(
                OTHER, field="reason_missed", field_required="reason_missed_other"
            )

        if self.validate_unscheduled_visit_reason:
            self.required_if(
                UNSCHEDULED, field="reason", field_required="reason_unscheduled"
            )

            self.required_if(
                OTHER,
                field="reason_unscheduled",
                field_required="reason_unscheduled_other",
            )

        self.required_if(OTHER, field="info_source", field_required="info_source_other")

    def metadata_exists_for(self, entry_status=None):
        """Returns True if metadata exists for this visit for
        the given entry_status.
        """
        appointment = self.cleaned_data.get("appointment")
        opts = dict(
            subject_identifier=appointment.subject_identifier,
            visit_code=appointment.visit_code,
            visit_code_sequence=appointment.visit_code_sequence,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            entry_status=entry_status or KEYED,
        )
        return (
            CrfMetadata.objects.filter(**opts).count()
            + RequisitionMetadata.objects.filter(**opts).count()
        )
