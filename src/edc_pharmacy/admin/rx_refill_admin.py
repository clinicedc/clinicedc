from django.conf import settings
from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from edc_model_admin import audit_fieldset_tuple
from edc_utils import formatted_age, get_utcnow

from ..admin_site import edc_pharmacy_admin
from ..forms import RxRefillForm
from ..models import RxRefill
from .dispensing_history_admin import DispensingHistoryInlineAdmin
from .model_admin_mixin import ModelAdminMixin


@admin.register(RxRefill, site=edc_pharmacy_admin)
class RxRefillAdmin(ModelAdminMixin, admin.ModelAdmin):

    show_object_tools = True

    autocomplete_fields = ["dosage_guideline", "formulation"]

    form = RxRefillForm

    model = RxRefill

    inlines = [DispensingHistoryInlineAdmin]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "rx",
                    "dosage_guideline",
                    "formulation",
                    "refill_date",
                    "number_of_days",
                )
            },
        ),
        (
            "Optional Customizations",
            {
                "description": "This section is only required if customizing the dosage guideline from above.",
                "fields": (
                    "dose",
                    "frequency",
                    "frequency_units",
                    "weight_in_kgs",
                ),
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

    list_display = (
        "subject_identifier",
        "refill_date",
        "description",
        "dispense",
        "returns",
        "prescription",
        "active",
        "packed",
        "shipped",
        "received_at_site",
        "verified",
        "verified_datetime",
    )
    list_filter = (
        "active",
        "refill_date",
        "visit_code",
        "visit_code_sequence",
        "packed",
        "shipped",
        "received_at_site",
        "site",
    )
    search_fields = [
        "id",
        "site__id",
        "rx__id",
        "rx__rando_sid",
        "rx__subject_identifier",
        "rx__registered_subject__initials",
        "dosage_guideline__medication__name",
    ]
    ordering = ["rx__subject_identifier", "-refill_date"]

    @admin.display(description="Subject identifier")
    def subject_identifier(self, obj=None):
        return obj.rx.subject_identifier

    @admin.display(description="Rx")
    def prescription(self, obj=None):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_rx_changelist")
        url = f"{url}?q={obj.rx.id}"
        context = dict(title="Back to RX", url=url, label="Rx")
        return render_to_string("dashboard_button.html", context=context)

    @admin.display
    def dispense(self, obj=None):
        add = True if not obj or obj.remaining is None else obj.remaining > 0
        if add:
            url = reverse("edc_pharmacy_admin:edc_pharmacy_dispensinghistory_add")
            url = f"{url}?rx_refill={obj.id}"
            disabled = ""
        else:
            url = "#"
            disabled = "disabled"
        context = dict(
            title="Dispense for this RX item",
            url=url,
            label="Dispense",
            disabled=disabled,
        )
        dispense_html = render_to_string("dashboard_button.html", context=context)
        url = reverse("edc_pharmacy_admin:edc_pharmacy_dispensinghistory_changelist")
        url = f"{url}?rx_refill={obj.id}"
        context = dict(
            title="Dispense history for this RX item", url=url, label="History"
        )
        dispense_history_html = render_to_string(
            "dashboard_button.html", context=context
        )
        return format_html(f"{dispense_html}<BR>{dispense_history_html}")

    @admin.display
    def returns(self, obj=None):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_returnhistory_add")
        url = f"{url}?rx_refill={obj.id}"
        context = dict(title="Returns for this RX item", url=url, label="Returns")
        returns_html = render_to_string("dashboard_button.html", context=context)
        url = reverse("edc_pharmacy_admin:edc_pharmacy_returnhistory_changelist")
        url = f"{url}?rx_refill={obj.id}"
        context = dict(
            title="Returns history for this RX item", url=url, label="History"
        )
        returns_history_html = render_to_string(
            "dashboard_button.html", context=context
        )
        return format_html(f"{returns_html}<BR>{returns_history_html}")

    @admin.display(description="Description of Refill")
    def description(self, obj=None):
        context = {
            "subject_identifier": obj.rx.registered_subject.subject_identifier,
            "initials": obj.rx.registered_subject.initials,
            "gender": obj.rx.registered_subject.gender,
            "age_in_years": formatted_age(
                born=obj.rx.registered_subject.dob, reference_dt=get_utcnow()
            ),
            "refill_date": obj.refill_date,
            "visit_code": obj.visit_code,
            "visit_code_sequence": obj.visit_code_sequence,
            "number_of_days": obj.number_of_days,
            "remaining": obj.remaining,
            "total": obj.total,
            "SHORT_DATE_FORMAT": settings.SHORT_DATE_FORMAT,
            "rx_refill": obj,
        }
        return render_to_string(
            f"edc_pharmacy/bootstrap{settings.EDC_BOOTSTRAP}/rx_refill_description.html",
            context,
        )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "rx" and request.GET.get("rx"):
            kwargs["queryset"] = db_field.related_model.objects.filter(
                pk=request.GET.get("rx", 0)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class RxRefillInlineAdmin(admin.StackedInline):

    form = RxRefillForm

    model = RxRefill

    fields = [
        "dosage_guideline",
        "formulation",
        "refill_date",
        "number_of_days",
        "dose",
        "frequency",
        "frequency_units",
    ]

    search_fields = ["dosage_guideline__medication__name"]
    ordering = ["refill_date"]
    extra = 0
