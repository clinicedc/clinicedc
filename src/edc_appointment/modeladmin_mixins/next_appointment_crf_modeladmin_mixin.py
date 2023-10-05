from django.apps import apps as django_apps
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django_audit_fields import audit_fieldset_tuple
from edc_crf.admin import crf_status_fieldset_tuple

from ..choices import APPT_DATE_INFO_SOURCES


class NextAppointmentCrfModelAdminMixin:
    fieldsets = (
        (None, {"fields": ("subject_visit", "report_datetime")}),
        (
            "Integrated Clinic",
            {
                "fields": (
                    "info_source",
                    "health_facility",
                    "appt_date",
                    "allow_create_interim",
                    "visitschedule",
                )
            },
        ),
        crf_status_fieldset_tuple,
        audit_fieldset_tuple,
    )

    radio_fields = {
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
