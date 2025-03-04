from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.translation import gettext_lazy as _
from edc_constants.constants import NO
from edc_form_validators import INVALID_ERROR, FormValidator

from ..constants import NEW_APPT
from ..utils import get_allow_skipped_appt_using, validate_date_is_on_clinic_day

if TYPE_CHECKING:
    from edc_facility.models import HealthFacility


class NextAppointmentCrfFormValidatorMixin(FormValidator):
    def __init__(self, **kwargs):
        self._clinic_days = None
        self._health_facility = None
        super().__init__(**kwargs)

    def clean(self):

        self.required_if(
            NO,
            field="offschedule_today",
            field_required="appt_date",
        )
        self.required_if(
            NO,
            field="offschedule_today",
            field_required="visitschedule",
        )

        self.required_if(
            NO,
            field="offschedule_today",
            field_required="health_facility",
        )

        self.required_if(
            NO,
            field="offschedule_today",
            field_required="health_facility",
        )

        if self.cleaned_data.get("appt_date") and self.cleaned_data.get("visitschedule"):
            self.validate_with_appointment_form_validator()
            self.validate_date_is_on_clinic_day()

    @property
    def visit_code_fld(self):
        if get_allow_skipped_appt_using():
            return get_allow_skipped_appt_using().get(self.model._meta.label_lower)[1]
        return "visitschedule"

    @property
    def visit_code(self):
        return getattr(
            self.cleaned_data.get(self.visit_code_fld),
            "visit_code",
            self.cleaned_data.get(self.visit_code_fld),
        )

    def validate_with_appointment_form_validator(self):
        # use AppointmentFormValidator to validate the next appt data
        from ..form_validators import AppointmentFormValidator as Base
        from ..models import Appointment

        class AppointmentFormValidator(Base):
            def validate_not_future_appt_datetime(self):
                pass

        try:
            instance = Appointment.objects.get(
                subject_identifier=self.related_visit.subject_identifier,
                visit_schedule_name=self.related_visit.visit_schedule_name,
                schedule_name=self.related_visit.schedule_name,
                visit_code=self.visit_code,
                visit_code_sequence=0,
            )
        except ObjectDoesNotExist:
            self.raise_validation_error(
                {
                    self.visit_code_fld: (
                        "Invalid selection. Expected "
                        f"{getattr(self.related_visit.appointment.next, 'visit_code', 'None')}"
                    )
                },
                INVALID_ERROR,
            )
        if instance == self.related_visit.appointment:
            self.raise_validation_error(
                {self.visit_code_fld: "Cannot be the current visit"}, INVALID_ERROR
            )

        if (
            instance.appt_status != NEW_APPT
            and instance.appt_datetime.date() != self.cleaned_data.get("appt_date")
        ):
            self.raise_validation_error(
                {"appt_date": "May not be changed. Next appointment has already started"},
                INVALID_ERROR,
            )

        cleaned_data = instance.__dict__
        cleaned_data.update(appt_datetime=self.appt_datetime)
        appointment_validator = AppointmentFormValidator(
            cleaned_data=cleaned_data,
            instance=instance,
            model=Appointment,
        )
        try:
            appointment_validator.validate()
        except ValidationError as e:
            if e.message_dict.get("appt_datetime"):
                raise ValidationError({"appt_date": e.message_dict["appt_datetime"]})
            else:
                raise

    @property
    def appt_datetime(self) -> datetime:
        return datetime(
            self.cleaned_data.get("appt_date").year,
            self.cleaned_data.get("appt_date").month,
            self.cleaned_data.get("appt_date").day,
            7,
            30,
            0,
            tzinfo=ZoneInfo("UTC"),
        )

    @property
    def clinic_days(self) -> list[int]:
        if not self._clinic_days:
            if self.cleaned_data.get("health_facility"):
                self._clinic_days = self.health_facility.clinic_days
        return self._clinic_days

    def validate_date_is_on_clinic_day(self):
        validate_date_is_on_clinic_day(
            cleaned_data=dict(
                appt_date=self.cleaned_data.get("appt_date"),
                report_datetime=self.cleaned_data.get("report_datetime"),
            ),
            clinic_days=self.clinic_days,
            raise_validation_error=self.raise_validation_error,
        )

    @property
    def health_facility(self) -> HealthFacility | None:
        if not self._health_facility:
            if self.cleaned_data.get("health_facility"):
                if self.cleaned_data.get("health_facility").site != self.related_visit.site:
                    raise self.raise_validation_error(
                        {"health_facility": "Invalid for this site"}, INVALID_ERROR
                    )
            else:
                raise self.raise_validation_error(
                    {"health_facility": _("This field is required.")}, INVALID_ERROR
                )
            self._health_facility = self.cleaned_data.get("health_facility")
        return self._health_facility
