from copy import deepcopy
from typing import List, Optional
from zoneinfo import ZoneInfo

from arrow import Arrow
from django import forms
from django.conf import settings
from edc_appointment.constants import MISSED_APPT
from edc_appointment.form_validators import WindowPeriodFormValidatorMixin
from edc_constants.constants import OTHER
from edc_form_validators import INVALID_ERROR, REQUIRED_ERROR, FormValidator
from edc_metadata.constants import KEYED
from edc_metadata.models import CrfMetadata, RequisitionMetadata
from edc_utils import formatted_datetime

from edc_visit_tracking.utils import get_subject_visit_missed_model_cls

from ..constants import MISSED_VISIT, SCHEDULED, UNSCHEDULED
from ..visit_sequence import VisitSequence, VisitSequenceError

EDC_VISIT_TRACKING_ALLOW_MISSED_UNSCHEDULED = getattr(
    settings, "EDC_VISIT_TRACKING_ALLOW_MISSED_UNSCHEDULED", False
)


class VisitFormValidator(WindowPeriodFormValidatorMixin, FormValidator):

    """Form validator for visit all models (e.g. subject_visit).

    See also `report_datetime` checks in the
    `VisitTrackingModelFormMixin`.
    """

    visit_sequence_cls = VisitSequence
    validate_missed_visit_reason = True
    validate_unscheduled_visit_reason = True

    def _clean(self) -> None:
        self.clean_defaults()
        super()._clean()

    def clean_defaults(self) -> None:
        if not self.cleaned_data.get("appointment"):
            raise forms.ValidationError(
                {"appointment": "This field is required"}, code=REQUIRED_ERROR
            )

        self.validate_visit_datetime_not_before_appointment()

        self.validate_visit_datetime_in_window_period()

        self.validate_visits_completed_in_order()

        self.validate_visit_code_sequence_and_reason()

        self.validate_visit_reason()

        self.required_if(OTHER, field="info_source", field_required="info_source_other")

    def validate_visit_datetime_not_before_appointment(
        self,
    ) -> None:
        """Asserts the report_datetime is not before the
        appt_datetime.
        """
        if report_datetime := self.cleaned_data.get("report_datetime"):
            tz = ZoneInfo(settings.TIME_ZONE)
            appt_datetime_local = Arrow.fromdatetime(
                self.cleaned_data.get("appointment").appt_datetime
            ).to(tz)
            if report_datetime.date() < appt_datetime_local.date():
                appt_datetime_str = formatted_datetime(
                    appt_datetime_local, format_as_date=True
                )
                self.raise_validation_error(
                    {
                        "report_datetime": (
                            "Invalid. Cannot be before appointment date. "
                            f"Got appointment date {appt_datetime_str}"
                        )
                    },
                    INVALID_ERROR,
                )

    def validate_visit_datetime_in_window_period(self):
        """Asserts the report_datetime is within the visits lower and
        upper boundaries of the visit_schedule.schdule.visit.

        See also `edc_visit_schedule`.
        """
        if self.cleaned_data.get("report_datetime"):
            super().validate_visit_datetime_in_window_period(
                self.cleaned_data.get("appointment"),
                self.cleaned_data.get("report_datetime"),
                "report_datetime",
            )

    def validate_visits_completed_in_order(self):
        """Asserts visits are completed in order."""
        visit_sequence = self.visit_sequence_cls(
            appointment=self.cleaned_data.get("appointment")
        )
        try:
            visit_sequence.enforce_sequence()
        except VisitSequenceError as e:
            raise forms.ValidationError(e, code=INVALID_ERROR)

    def validate_visit_code_sequence_and_reason(self) -> None:
        """Asserts the `reason` makes sense relative to the
        visit_code_sequence coming from the appointment.
        """
        appointment = self.cleaned_data.get("appointment")
        reason = self.cleaned_data.get("reason")
        if appointment:
            if not appointment.visit_code_sequence and reason == UNSCHEDULED:
                raise forms.ValidationError(
                    {"reason": "Invalid. This is not an unscheduled visit. See appointment."},
                    code=INVALID_ERROR,
                )
            if (
                appointment.visit_code_sequence
                and reason != UNSCHEDULED
                and EDC_VISIT_TRACKING_ALLOW_MISSED_UNSCHEDULED is False
            ):
                raise forms.ValidationError(
                    {"reason": "Invalid. This is an unscheduled visit. See appointment."},
                    code=INVALID_ERROR,
                )
            # raise if CRF metadata exist
            if reason == MISSED_VISIT and self.metadata_exists_for(
                entry_status=KEYED,
                exclude_models=[get_subject_visit_missed_model_cls()._meta.label_lower],
            ):
                raise forms.ValidationError(
                    {"reason": "Invalid. Some CRF data has already been submitted."},
                    code=INVALID_ERROR,
                )
            # raise if SubjectVisitMissed CRF metadata exist
            if reason in [UNSCHEDULED, SCHEDULED] and self.metadata_exists_for(
                entry_status=KEYED,
                filter_models=[get_subject_visit_missed_model_cls()._meta.label_lower],
            ):
                raise forms.ValidationError(
                    {"reason": "Invalid. A missed visit report has already been submitted."},
                    code=INVALID_ERROR,
                )

    def validate_visit_reason(self):
        """Asserts that reason=missed if appointment is missed"""
        if (
            self.cleaned_data.get("appointment").appt_timing == MISSED_APPT
            and self.cleaned_data.get("reason") != MISSED_VISIT
        ):
            self.raise_validation_error(
                {"reason": "Invalid. This is a missed visit. See appointment"}, INVALID_ERROR
            )

        if self.validate_missed_visit_reason:
            self.required_if(MISSED_VISIT, field="reason", field_required="reason_missed")

            self.required_if(
                OTHER, field="reason_missed", field_required="reason_missed_other"
            )

        if self.validate_unscheduled_visit_reason:
            if "reason_unscheduled" in self.cleaned_data:
                self.applicable_if(
                    UNSCHEDULED, field="reason", field_applicable="reason_unscheduled"
                )

                self.required_if(
                    OTHER,
                    field="reason_unscheduled",
                    field_required="reason_unscheduled_other",
                )

    def metadata_exists_for(
        self,
        entry_status: str = None,
        filter_models: Optional[List[str]] = None,
        exclude_models: Optional[List[str]] = None,
    ) -> bool:
        """Returns True if metadata exists for this visit for
        the given entry_status.
        """
        exclude_opts: dict = {}
        filter_opts = deepcopy(self.crf_filter_options)
        filter_opts.update(entry_status=entry_status or KEYED)
        if filter_models:
            filter_opts.update(model__in=filter_models)
        if exclude_models:
            exclude_opts.update(model__in=exclude_models)
        return (
            CrfMetadata.objects.filter(**filter_opts).exclude(**exclude_opts).count()
            + RequisitionMetadata.objects.filter(**filter_opts).exclude(**exclude_opts).count()
        )

    @property
    def crf_filter_options(self) -> dict:
        """Returns a dictionary of `filter` options when querying
        models CrfMetadata / RequisitionMetadata.
        """
        appointment = self.cleaned_data.get("appointment")
        return dict(
            subject_identifier=appointment.subject_identifier,
            visit_code=appointment.visit_code,
            visit_code_sequence=appointment.visit_code_sequence,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            entry_status=KEYED,
        )
