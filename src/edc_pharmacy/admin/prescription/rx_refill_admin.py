from typing import Tuple

from django.conf import settings
from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django_audit_fields.admin import audit_fieldset_tuple
from edc_appointment.models import Appointment
from edc_utils import convert_php_dateformat, formatted_age, get_utcnow

from ...admin_site import edc_pharmacy_admin
from ...forms import RxRefillForm
from ...models import RxRefill
from ..model_admin_mixin import ModelAdminMixin


@admin.register(RxRefill, site=edc_pharmacy_admin)
class RxRefillAdmin(ModelAdminMixin, admin.ModelAdmin):
    show_object_tools = True

    ordering: Tuple[str, ...] = ("refill_start_datetime",)

    autocomplete_fields = ["dosage_guideline", "formulation"]

    form = RxRefillForm

    model = RxRefill

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "rx",
                    "dosage_guideline",
                    "formulation",
                    "refill_start_datetime",
                    "refill_end_datetime",
                    "number_of_days",
                )
            },
        ),
        (
            "Optional Customizations",
            {
                "description": (
                    "This section is only required if customizing "
                    "the dosage guideline from above."
                ),
                "fields": ("weight_in_kgs",),
            },
        ),
        (
            "Notes",
            {"fields": ("notes",)},
        ),
        (
            "Verification",
            {"classes": ("collapse",), "fields": ("verified", "verified_datetime")},
        ),
        ("Calculations", {"classes": ("collapse",), "fields": ("total", "remaining")}),
        audit_fieldset_tuple,
    )

    list_display: Tuple[str, ...] = (
        "subject_identifier",
        "dashboard",
        "duration",
        "description",
        "prescription",
        "active",
        "packed",
        "shipped",
        "received_at_site",
        "verified",
        "verified_datetime",
    )

    list_filter: Tuple[str, ...] = (
        "active",
        "refill_start_datetime",
        "refill_end_datetime",
        "packed",
        "shipped",
        "received_at_site",
        "site",
    )

    search_fields: Tuple[str, ...] = (
        "id",
        "site__id",
        "rx__id",
        "rx__rando_sid",
        "rx__subject_identifier",
        "rx__registered_subject__initials",
        "dosage_guideline__medication__name",
    )

    @admin.display(description="Subject identifier")
    def subject_identifier(self, obj=None):
        return obj.rx.subject_identifier

    @admin.display(description="Duration")
    def duration(self, obj=None):
        refill_start_date = obj.refill_start_datetime.strftime(
            convert_php_dateformat(settings.DATE_FORMAT)
        ).split(" ")
        refill_end_date = (
            obj.refill_end_datetime.strftime(
                convert_php_dateformat(settings.DATE_FORMAT)
            ).split(" ")
            if obj.refill_end_datetime
            else "???"
        )
        context = dict(
            refill_start_date=format_html(
                "{}",
                mark_safe("&nbsp;".join(refill_start_date)),  # nosec B703, B308
            ),
            refill_end_date=format_html(
                "{}",
                mark_safe("&nbsp;".join(refill_end_date)),  # nosec B703, B308
            ),
            number_of_days=obj.number_of_days,
        )
        return render_to_string("edc_pharmacy/duration.html", context=context)

    @admin.display(description="Rx")
    def prescription(self, obj=None):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_rx_changelist")
        url = f"{url}?q={obj.rx.id}"
        context = dict(title="Back to RX", url=url, label="Rx")
        return render_to_string("edc_subject_dashboard/dashboard_button.html", context=context)

    @admin.display(description="Description of Refill")
    def description(self, obj=None):
        context = {
            "subject_identifier": obj.rx.registered_subject.subject_identifier,
            "initials": obj.rx.registered_subject.initials,
            "gender": obj.rx.registered_subject.gender,
            "age_in_years": formatted_age(
                born=obj.rx.registered_subject.dob, reference_dt=get_utcnow()
            ),
            "number_of_days": obj.number_of_days,
            "remaining": obj.remaining,
            "total": obj.total,
            "SHORT_DATE_FORMAT": settings.SHORT_DATE_FORMAT,
            "rx_refill": obj,
        }
        return render_to_string(
            "edc_pharmacy/rx_refill_description.html",
            context,
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "rx" and request.GET.get("rx"):
            kwargs["queryset"] = db_field.related_model.objects.filter(
                pk=request.GET.get("rx", 0)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_subject_dashboard_url_kwargs(self, obj):
        appointment = Appointment.objects.filter(
            subject_identifier=obj.subject_identifier,
            appt_datetime__date__gte=obj.refill_start_datetime.date(),
        ).first()
        return dict(
            subject_identifier=obj.subject_identifier,
            appointment=appointment.id,
        )


class RxRefillInlineAdmin(admin.StackedInline):
    form = RxRefillForm

    model = RxRefill

    fields: Tuple[str, ...] = (
        "dosage_guideline",
        "formulation",
        "refill_start_datetime",
        "refill_end_datetime",
        "number_of_days",
        "dose",
        "frequency",
        "frequency_units",
    )

    search_fields: Tuple[str, ...] = "dosage_guideline__medication__name"

    ordering: Tuple[str, ...] = ("refill_start_datetime",)

    extra = 0
