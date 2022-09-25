from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import TYPE_CHECKING, Any, List, Optional
from zoneinfo import ZoneInfo

from django import forms
from django.conf import settings
from edc_appointment.constants import MISSED_APPT
from edc_appointment.form_validators import (
    WindowPeriodFormValidatorMixin,
    validate_appt_datetime_unique,
)
from edc_constants.constants import OTHER
from edc_form_validators import INVALID_ERROR, REQUIRED_ERROR, FormValidator
from edc_metadata.constants import KEYED
from edc_metadata.utils import (
    get_crf_metadata_model_cls,
    get_requisition_metadata_model_cls,
)
from edc_utils import formatted_datetime
from edc_visit_schedule.utils import is_baseline

from ..constants import MISSED_VISIT, UNSCHEDULED
from ..utils import get_subject_visit_missed_model_cls
from ..visit_sequence import VisitSequence, VisitSequenceError

if TYPE_CHECKING:
    from edc_appointment.models import Appointment

EDC_VISIT_TRACKING_ALLOW_MISSED_UNSCHEDULED = getattr(
    settings, "EDC_VISIT_TRACKING_ALLOW_MISSED_UNSCHEDULED", False
)


class VisitFormValidator(WindowPeriodFormValidatorMixin, FormValidator):

    """Form validator for visit models (e.g. subject_visit).

    See also `report_datetime` checks in the
    `VisitTrackingCrfModelFormMixin`.
    """

    visit_sequence_cls = VisitSequence
    validate_missed_visit_reason = True
    validate_unscheduled_visit_reason = True

    def _clean(self) -> None:
        super()._clean()
        if not self.appointment:
            raise forms.ValidationError(
                {"appointment": "This field is required"}, code=REQUIRED_ERROR
            )

        validate_appt_datetime_unique(
            form_validator=self,
            appointment=self.appointment,
            appt_datetime=self.appointment.appt_datetime,
            form_field="appointment",
        )

        self.validate_visit_datetime_unique()

        self.validate_visit_datetime_not_before_appointment()

        self.validate_visit_datetime_matches_appt_datetime_at_baseline()

        self.validate_visit_datetime_in_window_period()

        self.validate_visits_completed_in_order()

        self.validate_visit_code_sequence_and_reason()

        self.validate_visit_reason()

        self.required_if(OTHER, field="info_source", field_required="info_source_other")

    @property
    def subject_identifier(self) -> str:
        return self.appointment.subject_identifier

    @property
    def appointment(self) -> Appointment:
        return self.cleaned_data.get("appointment")

    @property
    def report_datetime(self) -> datetime:
        """Returns report datetime in local timezone (from form
        cleaned_data).
        """
        return self.cleaned_data.get("report_datetime")

    @property
    def report_datetime_utc(self) -> datetime:
        """Returns report datetime in UTC timezone"""
        return self.report_datetime.astimezone(ZoneInfo("UTC"))

    @property
    def appt_datetime_local(self) -> datetime:
        """Returns appt datetime in local timezone"""
        return self.appointment.appt_datetime.astimezone(ZoneInfo(settings.TIME_ZONE))

    def validate_visit_datetime_unique(self: Any) -> None:
        """Assert one visit report per day"""
        if self.report_datetime:
            qs = self.instance.__class__.objects.filter(
                subject_identifier=self.subject_identifier,
                report_datetime__date=self.report_datetime_utc.date(),
                visit_schedule_name=self.instance.visit_schedule_name,
                schedule_name=self.instance.schedule_name,
            )
            if getattr(self.instance, "id"):
                qs = qs.exclude(id=self.instance.id)
            if qs.count() > 1:
                raise self.raise_validation_error(
                    {"report_datetime": "Visit report already exist for this date (M)"},
                    INVALID_ERROR,
                )
            elif qs.count() == 1:
                raise self.raise_validation_error(
                    {
                        "report_datetime": "A visit report already exists for this date. "
                        f"See {qs[0].visit_code}.{qs[0].visit_code_sequence}"
                    },
                    INVALID_ERROR,
                )

    def validate_visit_datetime_not_before_appointment(
        self,
    ) -> None:
        """Asserts the report_datetime is not before the
        appt_datetime.
        """
        if report_datetime_local := self.report_datetime:
            if report_datetime_local.date() < self.appt_datetime_local.date():
                appt_datetime_str = formatted_datetime(
                    self.appt_datetime_local, format_as_date=True
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

    def validate_visit_datetime_matches_appt_datetime_at_baseline(self) -> None:
        """Asserts the report_datetime matches the appt_datetime
        as baseline.
        """
        if is_baseline(instance=self.appointment):
            if report_datetime_local := self.report_datetime:
                if report_datetime_local.date() != self.appt_datetime_local.date():
                    appt_datetime_str = formatted_datetime(
                        self.appt_datetime_local, format_as_date=True
                    )
                    self.raise_validation_error(
                        {
                            "report_datetime": (
                                "Invalid. Must match appointment date at baseline. "
                                "If necessary, change the appointment date and try again. "
                                f"Got appointment date {appt_datetime_str}"
                            )
                        },
                        INVALID_ERROR,
                    )

    def validate_visit_datetime_in_window_period(self) -> None:
        """Asserts the report_datetime is within the visits lower and
        upper boundaries of the visit_schedule.schdule.visit.

        See also `edc_visit_schedule`.
        """
        if self.report_datetime:
            super().validate_visit_datetime_in_window_period(
                self.appointment,
                self.report_datetime,
                "report_datetime",
            )

    def validate_visits_completed_in_order(self) -> None:
        """Asserts visits are completed in order."""
        visit_sequence = self.visit_sequence_cls(appointment=self.appointment)
        try:
            visit_sequence.enforce_sequence()
        except VisitSequenceError as e:
            raise forms.ValidationError(e, code=INVALID_ERROR)

    def validate_visit_code_sequence_and_reason(self) -> None:
        """Asserts the `reason` makes sense relative to the
        visit_code_sequence coming from the appointment.
        """
        appointment = self.appointment
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

    def validate_visit_reason(self) -> None:
        """Asserts that reason=missed if appointment is missed"""
        if (
            self.appointment.appt_timing == MISSED_APPT
            and self.cleaned_data.get("reason") != MISSED_VISIT
        ):
            self.raise_validation_error(
                {"reason": "Invalid. This appointment was reported as missed"}, INVALID_ERROR
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
    ) -> int:
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
            get_crf_metadata_model_cls()
            .objects.filter(**filter_opts)
            .exclude(**exclude_opts)
            .count()
            + get_requisition_metadata_model_cls()
            .objects.filter(**filter_opts)
            .exclude(**exclude_opts)
            .count()
        )

    @property
    def crf_filter_options(self) -> dict:
        """Returns a dictionary of `filter` options when querying
        models CrfMetadata / RequisitionMetadata.
        """
        return dict(
            subject_identifier=self.subject_identifier,
            visit_code=self.appointment.visit_code,
            visit_code_sequence=self.appointment.visit_code_sequence,
            visit_schedule_name=self.appointment.visit_schedule_name,
            schedule_name=self.appointment.schedule_name,
            entry_status=KEYED,
        )
