from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django_audit_fields.admin import audit_fieldset_tuple

from edc_model_admin.history import SimpleHistoryAdmin
from edc_utils.date import to_local

from ...admin_site import edc_pharmacy_admin
from ...auth_objects import PHARMACY_SUPER_ROLE
from ...forms import OrderForm
from ...forms.stock import OrderFormSuper
from ...models import Order, OrderItem, Receive
from ..model_admin_mixin import ModelAdminMixin


@admin.register(Order, site=edc_pharmacy_admin)
class OrderAdmin(ModelAdminMixin, SimpleHistoryAdmin):
    change_list_title = "Pharmacy: Orders"
    change_form_title = "Pharmacy: Order"
    history_list_display = ()
    show_object_tools = True
    show_cancel = True
    list_per_page = 20

    form = OrderForm
    insert_before_fieldset = "Audit"
    ordering = ("-order_identifier",)

    fieldsets = (
        (
            None,
            {"fields": (["order_identifier", "order_datetime", "supplier", "title"])},
        ),
        ("Quantity", {"fields": (["item_count"])}),
        ("Status", {"fields": (["sent", "status"])}),
        ("Section C: Comment / Notes", {"fields": ("comment",)}),
        audit_fieldset_tuple,
    )

    list_display = (
        "identifier",
        "supplier",
        "short_title",
        "order_date",
        "status",
        "qty",
        "items",
        "receive_changelist",
        "created",
        "modified",
    )
    list_filter = ("sent", "status", "order_datetime")
    radio_fields = {"status": admin.VERTICAL}
    search_fields = ("id", "order_identifier", "title")
    readonly_fields = ("order_identifier", "sent")

    @admin.display(description="ORDER #", ordering="-order_identifier")
    def identifier(self, obj):
        return obj.order_identifier

    @admin.display(description="Title", ordering="title")
    def short_title(self, obj):
        return format_html(
            '<span title="{title}">{short_title}</span>',
            title=obj.title,
            short_title=obj.title[:20],
        )

    @admin.display(description="QTY", ordering="-item_count")
    def qty(self, obj):
        return obj.item_count

    @admin.display(description="Order items", ordering="-order_identifier")
    def items(self, obj):
        add_order_items_button = ""
        if obj.item_count > OrderItem.objects.filter(order=obj).count():
            url = reverse("edc_pharmacy_admin:edc_pharmacy_orderitem_add")
            next_url = "edc_pharmacy_admin:edc_pharmacy_order_changelist"
            url = f"{url}?next={next_url}&order={obj.id!s}&q={obj.order_identifier!s}"
            context = dict(url=url, label="Add order item")
            add_order_items_button = render_to_string(
                "edc_pharmacy/stock/items_as_button.html", context=context
            )
        count = OrderItem.objects.filter(order=obj).count()
        url = reverse("edc_pharmacy_admin:edc_pharmacy_orderitem_changelist")
        url = f"{url}?q={obj.order_identifier}"
        context = dict(
            url=url, label=f"Ordered items ({count})", title="Go to items on this order"
        )
        order_items_link = render_to_string(
            "edc_pharmacy/stock/items_as_link.html", context=context
        )
        rendered = [add_order_items_button, order_items_link]
        return format_html(
            "{}",
            mark_safe("<BR>".join([r for r in rendered if r])),  # nosec B703, B308
        )

    @admin.display(description="Order date", ordering="order_datetime")
    def order_date(self, obj):
        return to_local(obj.order_datetime).date()

    @admin.display(description="Receive #")
    def receive_changelist(self, obj):
        try:
            rcv_obj = Receive.objects.get(order=obj)
        except ObjectDoesNotExist:
            pass
        else:
            url = reverse("edc_pharmacy_admin:edc_pharmacy_receive_changelist")
            url = f"{url}?q={rcv_obj.receive_identifier!s}"
            context = dict(url=url, label=rcv_obj.receive_identifier, title="Receive #")
            return render_to_string("edc_pharmacy/stock/items_as_link.html", context=context)
        return None

    def get_form(self, request, obj=None, **kwargs):
        try:
            request.user.userprofile.roles.get(name=PHARMACY_SUPER_ROLE)
        except ObjectDoesNotExist:
            pass
        else:
            self.form = OrderFormSuper
        return super().get_form(request, obj, **kwargs)
