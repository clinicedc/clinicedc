from __future__ import annotations

from datetime import datetime
from logging import warning
from typing import TYPE_CHECKING, Any

from django.apps import apps as django_apps
from django.conf import settings
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from edc_consent import NotConsentedError
from edc_consent.requires_consent import RequiresConsent
from edc_consent.site_consents import SiteConsentError, site_consents
from edc_facility.utils import get_facilities
from edc_form_validators import INVALID_ERROR
from edc_form_validators.form_validator import FormValidator
from edc_metadata.metadata_helper import MetadataHelperMixin
from edc_registration import get_registered_subject_model_cls
from edc_utils import formatted_datetime, get_utcnow, to_utc
from edc_utils.date import to_local
from edc_visit_schedule.site_visit_schedules import site_visit_schedules
from edc_visit_schedule.subject_schedule import NotOnScheduleError
from edc_visit_schedule.utils import get_onschedule_model_instance, is_baseline

from ..appointment_reason_updater import AppointmentReasonUpdater
from ..constants import (
    CANCELLED_APPT,
    COMPLETE_APPT,
    IN_PROGRESS_APPT,
    INCOMPLETE_APPT,
    MISSED_APPT,
    NEW_APPT,
    SKIPPED_APPT,
    UNSCHEDULED_APPT,
)
from ..exceptions import (
    AppointmentBaselineError,
    AppointmentReasonUpdaterCrfsExistsError,
    AppointmentReasonUpdaterError,
    AppointmentReasonUpdaterRequisitionsExistsError,
    UnscheduledAppointmentError,
)
from ..form_validator_mixins import WindowPeriodFormValidatorMixin
from ..utils import (
    get_allow_skipped_appt_using,
    get_previous_appointment,
    raise_on_appt_may_not_be_missed,
)
from .utils import validate_appt_datetime_unique

if TYPE_CHECKING:
    from ..models import Appointment

INVALID_APPT_DATE = "invalid_appt_datetime"
INVALID_APPT_STATUS = "invalid_appt_status"
INVALID_APPT_REASON = "invalid_appt_reason"
INVALID_PREVIOUS_APPOINTMENT_NOT_UPDATED = "previous_appointment_not_updated"
INVALID_PREVIOUS_VISIT_MISSING = "previous_visit_missing"
INVALID_MISSED_APPT_NOT_ALLOWED = "invalid_missed_appt_not_allowed"
INVALID_APPT_STATUS_AT_BASELINE = "invalid_appt_status_at_baseline"
INVALID_SKIPPED_APPT_NOT_ALLOWED_AT_BASELINE = "invalid_skipped_appt_not_allowed_at_baseline"
INVALID_APPT_TIMING = "invalid_appt_timing"
INVALID_APPT_TIMING_CRFS_EXIST = "invalid_appt_timing_crfs_exist"
INVALID_APPT_TIMING_REQUISITIONS_EXIST = "invalid_appt_timing_requisitions_exist"


class AppointmentFormValidator(
    MetadataHelperMixin, WindowPeriodFormValidatorMixin, FormValidator
):
    """Note, the appointment is only changed, never added,
    through the AppointmentForm.
    """

    appointment_model = "edc_appointment.appointment"

    def clean(self: Any):
        # TODO: do not allow a missed appt (in window) to be followed by an unscheduled appt
        #  that is also within window.
        self.validate_scheduled_parent_not_missed()
        if self.cleaned_data.get("appt_status") in [CANCELLED_APPT, SKIPPED_APPT]:
            self.validate_appt_status_if_skipped()
            self.validate_appt_new_or_cancelled_or_skipped()
            self.validate_appt_inprogress_or_incomplete()
        else:
            self.validate_appt_sequence()
            self.validate_visit_report_sequence()
            self.validate_timepoint()
            validate_appt_datetime_unique(
                form_validator=self,
                appointment=self.instance,
                appt_datetime=self.cleaned_data.get("appt_datetime"),
            )
            self.validate_appt_datetime_not_before_consent_datetime()
            self.validate_appt_datetime_not_after_next_appt_datetime()
            self.validate_not_future_appt_datetime()
            self.validate_appt_datetime_in_window_period(
                self.instance,
                self.cleaned_data.get("appt_datetime"),
                "appt_datetime",
            )
            self.validate_subject_on_schedule()
            self.validate_appt_reason()
            self.validate_appt_incomplete_and_visit_report()
            self.validate_appt_new_or_cancelled_or_skipped()
            self.validate_appt_inprogress_or_incomplete()
            self.validate_appt_new_or_complete()

            self.validate_facility_name()
        self.validate_appt_type()
        self.validate_appointment_timing()

    @property
    def appointment_model_cls(self) -> Appointment:
        return django_apps.get_model(self.appointment_model)

    @property
    def required_additional_forms_exist(self) -> bool:
        """Returns True if any `additional` required forms are
        yet to be keyed.

        Concept of "additional forms" not in use.
        """
        return False

    def validate_visit_report_sequence(self: Any) -> bool:
        """Enforce visit report sequence."""
        if self.cleaned_data.get("appt_status") == IN_PROGRESS_APPT and getattr(
            self.instance, "id", None
        ):
            previous_appt = get_previous_appointment(self.instance, include_interim=True)
            if previous_appt and previous_appt.appt_status not in [
                CANCELLED_APPT,
                SKIPPED_APPT,
            ]:
                if not previous_appt.related_visit:
                    self.raise_validation_error(
                        message=(
                            "A previous appointment requires a visit report. "
                            f"Update appointment {previous_appt.visit_code}."
                            f"{previous_appt.visit_code_sequence} first."
                        ),
                        error_code=INVALID_PREVIOUS_VISIT_MISSING,
                    )
        return True

    def validate_appt_sequence(self: Any) -> bool:
        """Enforce appointment follows sequence of
        timepoint + visit_code_sequence.

        Check if previous appointment appt_status is NEW_APPT

        """
        if self.cleaned_data.get("appt_status") in [
            IN_PROGRESS_APPT,
            INCOMPLETE_APPT,
            COMPLETE_APPT,
        ]:
            if self.instance.previous:
                if obj := (
                    self.appointment_model_cls.objects.filter(
                        subject_identifier=self.instance.subject_identifier,
                        visit_schedule_name=self.instance.visit_schedule_name,
                        schedule_name=self.instance.schedule_name,
                        appt_status=NEW_APPT,
                        appt_datetime__lt=self.instance.appt_datetime,
                    )
                    .order_by("timepoint", "visit_code_sequence")
                    .first()
                ):
                    self.raise_validation_error(
                        {
                            "__all__": _(
                                "A previous appointment requires updating. "
                                f"Update appointment {obj.visit_code}."
                                f"{obj.visit_code_sequence} first."
                            )
                        },
                        INVALID_PREVIOUS_APPOINTMENT_NOT_UPDATED,
                    )
        return True

    def validate_timepoint(self: Any):
        visit_schedule = site_visit_schedules.get_visit_schedule(
            self.instance.visit_schedule_name
        )
        schedule = visit_schedule.schedules.get(self.instance.schedule_name)
        visit = schedule.visits.get(self.instance.visit_code)
        if visit and self.instance.timepoint != visit.timepoint:
            self.raise_validation_error(
                f"Invalid timepoint. Expected {visit.timepoint} "
                f"for visit_code={visit.visit_code}. Got {self.instance.timepoint}"
            )

    def validate_not_future_appt_datetime(self: Any) -> None:
        appt_datetime = self.cleaned_data.get("appt_datetime")
        appt_status = self.cleaned_data.get("appt_status")
        if appt_datetime and appt_status != NEW_APPT:
            if to_utc(appt_datetime) > get_utcnow():
                self.raise_validation_error(
                    {"appt_datetime": "Cannot be a future date/time."},
                    INVALID_APPT_DATE,
                )

    def validate_appt_datetime_not_before_consent_datetime(self: Any) -> None:
        if (
            "edc_consent" not in settings.INSTALLED_APPS
            and "edc_consent.apps.AppConfig" not in settings.INSTALLED_APPS
        ):
            warning(
                "Skipping consent_datetime form validation. "
                "`edc_consent` not in `INSTALLED_APPS`"
            )
        else:
            appt_datetime = self.cleaned_data.get("appt_datetime")
            appt_status = self.cleaned_data.get("appt_status")
            if appt_datetime and appt_status != NEW_APPT:
                consent_datetime = self.consent_datetime_or_raise(to_utc(appt_datetime))
                if to_utc(appt_datetime).date() < consent_datetime.date():
                    formatted_date = formatted_datetime(
                        to_local(consent_datetime), format_as_date=True
                    )
                    self.raise_validation_error(
                        {
                            "appt_datetime": (
                                (
                                    "Invalid. Cannot be before consent date. "
                                    f"Got consented on {formatted_date}"
                                )
                            )
                        },
                        INVALID_APPT_DATE,
                    )

    def validate_appointment_timing(self) -> None:
        """Checks the subject visit report (if it exists) is missed or scheduled
        based on appt_timing OR raises

        Also handles SKIPPED_APPT, if enabled in settings,
        see also `utils.get_allow_skipped_appt_using`.

        Data is not updated here (commit=False), see the model_mixin save().
        """

        self.not_applicable_if(
            SKIPPED_APPT, field="appt_status", field_applicable="appt_timing"
        )
        try:
            raise_on_appt_may_not_be_missed(
                appointment=self.instance, appt_timing=self.cleaned_data.get("appt_timing")
            )
        except AppointmentBaselineError as e:
            self.raise_validation_error(
                {"appt_timing": str(e)}, INVALID_APPT_STATUS_AT_BASELINE
            )
        except UnscheduledAppointmentError as e:
            self.raise_validation_error(
                {"appt_timing": str(e)}, INVALID_MISSED_APPT_NOT_ALLOWED
            )

        try:
            AppointmentReasonUpdater(
                appointment=self.instance,
                appt_timing=self.cleaned_data.get("appt_timing"),
                appt_reason=self.cleaned_data.get("appt_reason"),
                commit=False,
            )
        except AppointmentReasonUpdaterCrfsExistsError as e:
            self.raise_validation_error(
                {"appt_timing": str(e)}, INVALID_APPT_TIMING_CRFS_EXIST
            )
        except AppointmentReasonUpdaterRequisitionsExistsError as e:
            self.raise_validation_error(
                {"appt_timing": str(e)}, INVALID_APPT_TIMING_REQUISITIONS_EXIST
            )
        except AppointmentReasonUpdaterError as e:
            self.raise_validation_error({"appt_timing": str(e)}, INVALID_APPT_TIMING)

    def validate_appt_datetime_not_after_next_appt_datetime(self: Any) -> None:
        appt_datetime = self.cleaned_data.get("appt_datetime")
        appt_status = self.cleaned_data.get("appt_status")
        if appt_datetime and appt_status and appt_status != NEW_APPT:
            if self.instance.relative_next:
                if to_utc(appt_datetime) > self.instance.relative_next.appt_datetime:
                    formatted_date = formatted_datetime(
                        self.instance.relative_next.appt_datetime
                    )
                    self.raise_validation_error(
                        {
                            "appt_datetime": (
                                "Cannot be after next appointment. Next appointment is "
                                f"{self.instance.relative_next.visit_label} "
                                f"on {formatted_date}."
                            )
                        },
                        INVALID_APPT_DATE,
                    )

    def validate_appt_incomplete_and_visit_report(self: Any) -> None:
        """Require a visit report, at least, if wanting to set appt_status
        to INCOMPLETE_APPT"""
        appt_status = self.cleaned_data.get("appt_status")
        if appt_status == INCOMPLETE_APPT and not self.instance.visit:
            self.raise_validation_error(
                {"appt_status": "Invalid. A visit report has not been submitted."},
                INVALID_APPT_STATUS,
            )

    def validate_appt_new_or_cancelled_or_skipped(self: Any) -> None:
        """Don't allow new or cancelled if form data exists
        and don't allow cancelled if visit_code_sequence == 0.
        """
        appt_status = self.cleaned_data.get("appt_status")
        if self.instance.visit_code_sequence == 0 and appt_status == CANCELLED_APPT:
            self.raise_validation_error(
                {"appt_status": "Invalid. A scheduled appointment may not be cancelled."},
                INVALID_APPT_STATUS,
            )
        elif self.instance.visit_code_sequence != 0 and appt_status == SKIPPED_APPT:
            self.raise_validation_error(
                {"appt_status": "Invalid. An unscheduled appointment may not be skipped."},
                INVALID_APPT_STATUS,
            )
        elif is_baseline(self.instance) and appt_status == SKIPPED_APPT:
            self.raise_validation_error(
                {"appt_status": "Invalid. Baseline appointment may not be skipped."},
                INVALID_APPT_STATUS,
            )
        elif (
            appt_status in [NEW_APPT, CANCELLED_APPT, SKIPPED_APPT]
            and self.crf_metadata_keyed_exists
        ):
            self.raise_validation_error(
                {"appt_status": "Invalid. CRF data has already been entered."},
                INVALID_APPT_STATUS,
            )
        elif (
            appt_status in [NEW_APPT, CANCELLED_APPT, SKIPPED_APPT]
            and self.requisition_metadata_keyed_exists
        ):
            self.raise_validation_error(
                {"appt_status": "Invalid. requisition data has already been entered."},
                INVALID_APPT_STATUS,
            )

    def validate_appt_inprogress_or_incomplete(self: Any) -> None:
        appt_status = self.cleaned_data.get("appt_status")
        if appt_status in [CANCELLED_APPT, SKIPPED_APPT] and self.crf_metadata_keyed_exists:
            self.raise_validation_error(
                {"appt_status": format_html("Invalid. Some CRFs have already been keyed")},
                INVALID_APPT_STATUS,
            )
        elif (
            appt_status in [CANCELLED_APPT, SKIPPED_APPT]
            and self.requisition_metadata_keyed_exists
        ):
            self.raise_validation_error(
                {
                    "appt_status": format_html(
                        "Invalid. Some requisitions have already been keyed"
                    )
                },
                INVALID_APPT_STATUS,
            )

        elif (
            appt_status
            not in [INCOMPLETE_APPT, IN_PROGRESS_APPT, CANCELLED_APPT, SKIPPED_APPT]
            and self.crf_metadata_required_exists
        ):
            url = self.changelist_url("crfmetadata")
            self.raise_validation_error(
                {
                    "appt_status": format_html(
                        f'Invalid. Not all <a href="{url}">required CRFs</a> have been keyed'
                    )
                },
                INVALID_APPT_STATUS,
            )
        elif (
            appt_status
            not in [INCOMPLETE_APPT, IN_PROGRESS_APPT, CANCELLED_APPT, SKIPPED_APPT]
            and self.requisition_metadata_required_exists
        ):
            url = self.changelist_url("requisitionmetadata")
            self.raise_validation_error(
                {
                    "appt_status": format_html(
                        f'Invalid. Not all <a href="{url}">'
                        "required requisitions</a> have been keyed"
                    )
                },
                INVALID_APPT_STATUS,
            )

    def validate_appt_inprogress(self: Any) -> None:
        appt_status = self.cleaned_data.get("appt_status")
        if appt_status == IN_PROGRESS_APPT and self.appointment_in_progress_exists:
            self.raise_validation_error(
                {
                    "appt_status": (
                        "Invalid. Another appointment in this schedule is in progress."
                    )
                },
                INVALID_APPT_STATUS,
            )

    def validate_appt_new_or_complete(self: Any) -> None:
        appt_status = self.cleaned_data.get("appt_status")
        if (
            appt_status not in [COMPLETE_APPT, NEW_APPT, IN_PROGRESS_APPT]
            and self.crf_metadata_exists
            and self.requisition_metadata_exists
            and not self.crf_metadata_required_exists
            and not self.requisition_metadata_required_exists
            and not self.required_additional_forms_exist
        ):
            if not self.crf_metadata_required_exists:
                self.raise_validation_error(
                    {"appt_status": "Invalid. All required CRFs have been keyed"},
                    INVALID_APPT_STATUS,
                )
            elif not self.requisition_metadata_required_exists:
                self.raise_validation_error(
                    {"appt_status": "Invalid. All required requisitions have been keyed"},
                    INVALID_APPT_STATUS,
                )
            elif not self.required_additional_forms_exist:
                self.raise_validation_error(
                    {
                        "appt_status": (
                            "Invalid. All required 'additional' forms have been keyed"
                        )
                    },
                    INVALID_APPT_STATUS,
                )

    @property
    def appointment_in_progress_exists(self: Any) -> None:
        """Returns True if another appointment in this schedule
        is currently set to "in_progress".
        """
        return (
            self.appointment_model_cls.objects.filter(
                subject_identifier=self.instance.subject_identifier,
                visit_schedule_name=self.instance.visit_schedule_name,
                schedule_name=self.instance.schedule_name,
                appt_status=IN_PROGRESS_APPT,
            )
            .exclude(id=self.instance.id)
            .exists()
        )

    def validate_appt_status_if_skipped(self):
        """Raises validation error by default"""
        if self.cleaned_data.get("appt_status") == SKIPPED_APPT:
            if not get_allow_skipped_appt_using():
                self.raise_validation_error(
                    {"appt_status": "Invalid. Appointment may not be skipped"},
                    INVALID_APPT_STATUS,
                )
            elif is_baseline(self.instance):
                self.raise_validation_error(
                    {"appt_status": "Invalid. Appointment may not be skipped at baseline"},
                    INVALID_APPT_STATUS_AT_BASELINE,
                )

    def validate_facility_name(self: Any) -> None:
        """Raises if facility_name not found in edc_facility.AppConfig.

        Is this still used?
        """
        if self.cleaned_data.get("facility_name"):
            if self.cleaned_data.get("facility_name") not in get_facilities():
                self.raise_validation_error(
                    {"__all__": f"Facility '{self.facility_name}' does not exist."},
                    INVALID_ERROR,
                )

    def validate_appt_type(self):
        self.not_applicable_if(SKIPPED_APPT, field="appt_status", field_applicable="appt_type")

    def validate_appt_reason(self: Any) -> None:
        """Raises if visit_code_sequence is not 0 and appt_reason
        is not UNSCHEDULED_APPT.
        """
        appt_reason = self.cleaned_data.get("appt_reason")
        appt_status = self.cleaned_data.get("appt_status")
        if (
            appt_reason
            and self.instance.visit_code_sequence
            and appt_reason != UNSCHEDULED_APPT
        ):
            self.raise_validation_error(
                {"appt_reason": f"Expected {UNSCHEDULED_APPT.title()}"}, INVALID_APPT_REASON
            )
        elif (
            appt_reason
            and not self.instance.visit_code_sequence
            and appt_reason == UNSCHEDULED_APPT
        ):
            self.raise_validation_error(
                {"appt_reason": f"Cannot be {UNSCHEDULED_APPT.title()}"}, INVALID_APPT_REASON
            )
        elif (
            appt_status
            and not self.instance.visit_code_sequence
            and appt_status == CANCELLED_APPT
        ):
            self.raise_validation_error(
                {"appt_status": "Invalid. A scheduled appointment cannot be cancelled"},
                INVALID_APPT_STATUS,
            )
        elif appt_status and self.instance.visit_code_sequence and appt_status == SKIPPED_APPT:
            self.raise_validation_error(
                {"appt_status": "Invalid. An unscheduled appointment cannot be skipped"},
                INVALID_APPT_STATUS,
            )

    def validate_scheduled_parent_not_missed(self):
        if (
            self.cleaned_data.get("appt_reason") == UNSCHEDULED_APPT
            and get_previous_appointment(self.instance, include_interim=True)
            and get_previous_appointment(self.instance, include_interim=True).appt_status
            == MISSED_APPT
        ):
            self.raise_validation_error(
                {
                    "__all__": "Please completed the scheduled appointment instead. "
                    f"See {self.instance.previous.visit_code}."
                    f"{self.instance.previous.visit_code_sequence}"
                },
                INVALID_APPT_STATUS,
            )

    def changelist_url(self: Any, model_name: str) -> Any:
        """Returns the model's changelist url with filter querystring"""
        url = reverse(f"edc_metadata_admin:edc_metadata_{model_name}_changelist")
        url = (
            f"{url}?q={self.instance.subject_identifier}"
            f"&visit_code={self.instance.visit_code}"
            f"&visit_code_sequence={self.instance.visit_code_sequence}"
        )
        return url

    def consent_datetime_or_raise(self: Any, appt_datetime: datetime) -> datetime:
        consent_model = site_visit_schedules.get_consent_model(
            visit_schedule_name=self.instance.visit_schedule_name,
            schedule_name=self.instance.schedule_name,
        )
        try:
            RequiresConsent(
                model=self.instance._meta.label_lower,
                subject_identifier=self.instance.subject_identifier,
                report_datetime=appt_datetime,
                consent_model=consent_model,
            )
        except SiteConsentError:
            self.raise_validation_error(
                {
                    "appt_datetime": (
                        "Date does not fall within any configured consent period."
                        f"Expected one of {site_consents.consents}. "
                        "See the EDC configuration."
                    )
                },
                INVALID_APPT_DATE,
            )
        except NotConsentedError as e:
            self.raise_validation_error(
                {"appt_datetime": str(e)},
                INVALID_APPT_DATE,
            )
        registered_subject = get_registered_subject_model_cls().objects.get(
            subject_identifier=self.instance.subject_identifier
        )
        return registered_subject.consent_datetime

    def validate_subject_on_schedule(self: Any) -> None:
        if self.cleaned_data.get("appt_datetime"):
            appt_datetime = self.cleaned_data.get("appt_datetime")
            subject_identifier = self.instance.subject_identifier
            onschedule_model = site_visit_schedules.get_onschedule_model(
                visit_schedule_name=self.instance.visit_schedule_name,
                schedule_name=self.instance.schedule_name,
            )
            qs = django_apps.get_model(onschedule_model).objects.filter(
                subject_identifier=subject_identifier,
            )

            try:
                get_onschedule_model_instance(
                    subject_identifier=subject_identifier,
                    visit_schedule_name=self.instance.visit_schedule_name,
                    schedule_name=self.instance.schedule_name,
                    reference_datetime=to_utc(appt_datetime),
                )
            except NotOnScheduleError:
                self.raise_validation_error(
                    (
                        "Subject is not on a schedule for the given date and time. "
                        f"Expected one of {[str(obj) for obj in qs.all()]}. "
                        "Check the appointment date and/or time"
                    ),
                    INVALID_APPT_DATE,
                )
