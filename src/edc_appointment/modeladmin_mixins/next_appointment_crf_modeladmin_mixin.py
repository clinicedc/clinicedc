from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django_audit_fields import audit_fieldset_tuple
from edc_constants.constants import PATIENT
from edc_crf.admin import crf_status_fieldset_tuple
from edc_utils.date import to_local
from edc_visit_schedule.models import VisitSchedule
from edc_visit_tracking.utils import get_related_visit_model_cls

from ..choices import APPT_DATE_INFO_SOURCES

if TYPE_CHECKING:
    from edc_facility.models import HealthFacility

__all__ = ["NextAppointmentCrfModelAdminMixin"]


class NextAppointmentCrfModelAdminMixin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("subject_visit", "report_datetime")}),
        (
            "Appointment",
            {
                "fields": (
                    "offschedule_today",
                    "appt_date",
                )
            },
        ),
        (
            "Appointment (Details)",
            {
                "fields": (
                    "visitschedule",
                    "health_facility",
                )
            },
        ),
        crf_status_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = {
        "offschedule_today": admin.VERTICAL,
        "crf_status": admin.VERTICAL,
        "info_source": admin.VERTICAL,
    }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "visitschedule":
            visit_schedule_model_cls = django_apps.get_model(
                "edc_visit_schedule.visitschedule"
            )
            try:
                related_visit = self.related_visit(request)
            except ObjectDoesNotExist:
                kwargs["queryset"] = visit_schedule_model_cls.objects.none()
            else:
                kwargs["queryset"] = visit_schedule_model_cls.objects.filter(
                    visit_schedule_name=related_visit.visit_schedule_name,
                    schedule_name=related_visit.schedule_name,
                    active=True,
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "info_source":
            kwargs["choices"] = APPT_DATE_INFO_SOURCES
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        # try to get next appointment
        try:
            related_visit = get_related_visit_model_cls().objects.get(
                id=initial.get("subject_visit")
            )
        except ObjectDoesNotExist:
            pass
        else:
            if next_appt := related_visit.appointment.next:
                initial.update(
                    info_source=self.get_default_info_source(request),
                    health_facility=self.get_default_health_facility(next_appt),
                    appt_date=to_local(next_appt.appt_datetime).date(),
                    appt_datetime=to_local(next_appt.appt_datetime),
                    visitschedule=VisitSchedule.objects.get(
                        visit_schedule_name=next_appt.visit_schedule_name,
                        schedule_name=next_appt.schedule_name,
                        visit_code=next_appt.visit_code,
                    ),
                )
        return initial

    def get_default_health_facility(self, next_appt) -> HealthFacility:
        return django_apps.get_model("edc_facility.healthfacility").objects.get(
            site=next_appt.site
        )

    def get_default_info_source(self, request):
        return django_apps.get_model("edc_appointment.infosources").objects.get(name=PATIENT)
