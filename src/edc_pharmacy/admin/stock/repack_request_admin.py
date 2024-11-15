from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect
from django.template.loader import render_to_string
from django.urls import reverse
from django_audit_fields import audit_fieldset_tuple
from edc_utils.date import to_local

from ...admin_site import edc_pharmacy_admin
from ...forms import RepackRequestForm
from ...models import RepackRequest
from ...utils import format_qty
from ..actions import confirm_repacked_stock_action, print_labels_from_repack_request
from ..model_admin_mixin import ModelAdminMixin


@admin.register(RepackRequest, site=edc_pharmacy_admin)
class RequestRepackAdmin(ModelAdminMixin, admin.ModelAdmin):
    change_list_title = "Pharmacy: Repackage request"
    change_form_title = "Pharmacy: Repack"
    show_object_tools = True
    show_cancel = True
    list_per_page = 20

    autocomplete_fields = ["from_stock", "container"]
    form = RepackRequestForm
    actions = [print_labels_from_repack_request, confirm_repacked_stock_action]

    change_list_note = render_to_string(
        "edc_pharmacy/stock/instructions/repack_instructions.html"
    )

    fieldsets = (
        (
            "Section A: Repack",
            {
                "fields": (
                    "repack_identifier",
                    "repack_datetime",
                    "from_stock",
                    "container",
                    "qty",
                    "processed",
                )
            },
        ),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "repack_date",
        "from_stock_changelist",
        "formatted_qty",
        "container",
        "from_stock__product__name",
        "processed",
        "stock_changelist",
    )

    search_fields = (
        "id",
        "container__name",
        "from_stock__code",
    )

    @admin.display(description="Repack date", ordering="repack_datetime")
    def repack_date(self, obj):
        return to_local(obj.repack_datetime).date()

    @admin.display(description="Stock")
    def stock_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")
        url = f"{url}?q={obj.id}"
        context = dict(url=url, label="Stock", title="Go to stock")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="From stock")
    def from_stock_changelist(self, obj):
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stock_changelist")
        url = f"{url}?q={obj.from_stock.code}"
        context = dict(url=url, label=obj.from_stock.code, title="Go to stock")
        return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)

    @admin.display(description="REPACK #", ordering="-repack_identifier")
    def identifier(self, obj):
        return obj.repack_identifier

    @admin.display(description="QTY", ordering="qty")
    def formatted_qty(self, obj):
        return format_qty(obj.qty, obj.container)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.processed:
            f = [
                "repack_identifier",
                "repack_datetime",
                "container",
                "from_stock",
                "processed",
                "qty",
            ]
            return self.readonly_fields + tuple(f)
        return self.readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "from_stock" and request.GET.get("from_stock"):
            kwargs["queryset"] = db_field.related_model.objects.filter(
                pk=request.GET.get("from_stock", 0)
            )
            kwargs["widget"] = AutocompleteSelect(
                db_field.remote_field, self.admin_site, using=kwargs.get("using")
            )

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
