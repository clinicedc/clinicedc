from django.contrib import admin

from ..admin_site import edc_pharmacy_admin
from ..forms import OrderForm
from ..models import Order
from .model_admin_mixin import ModelAdminMixin


@admin.register(Order, site=edc_pharmacy_admin)
class OrderAdmin(ModelAdminMixin, admin.ModelAdmin):
    show_object_tools = True

    # autocomplete_fields = (
    #     "dosage_guideline",
    #     "formulation",
    # )

    form = OrderForm

    # fieldsets = (
    #     (
    #         "Order",
    #         {
    #             "fields": (
    #                 "stock",
    #                 "qty",
    #             ),
    #         },
    #     ),
    #     (
    #         "Order status",
    #         {
    #             "fields": (
    #                 "packed",
    #                 "packed_datetime",
    #                 "shipped",
    #                 "shipped_datetime",
    #                 "received_at_site",
    #                 "received_at_site_datetime",
    #             ),
    #         },
    #     ),
    #     (
    #         "Refill",
    #         {
    #             "fields": (
    #                 "rx",
    #                 "dosage_guideline",
    #                 "formulation",
    #                 "order_datetime",
    #             )
    #         },
    #     ),
    #     audit_fieldset_tuple,
    # )
    #
    # list_display = (
    #     "subject_identifier",
    #     "order_datetime",
    #     "description",
    #     "packed",
    #     "shipped",
    #     "received_at_site",
    # )
    # list_filter = (
    #     "packed",
    #     "shipped",
    #     "received_at_site",
    #     "order_datetime",
    #     "visit_code",
    #     "visit_code_sequence",
    #     "site",
    # )
    # search_fields = (
    #     "id",
    #     "site__id",
    #     "rx__id",
    #     "rx__rando_sid",
    #     "rx__subject_identifier",
    #     "rx__registered_subject__initials",
    #     "dosage_guideline__medication__name",
    # )
    # ordering = (
    #     "rx__subject_identifier",
    #     "-refill_date",
    # )
    #
    # readonly_fields = (
    #     "rx",
    #     "dosage_guideline",
    #     "formulation",
    #     "refill_date",
    #     "number_of_days",
    #     "packed",
    #     "shipped",
    #     "received_at_site",
    # )
    #
    # @staticmethod
    # def description(obj):
    #     dob = obj.rx.registered_subject.dob.strftime(
    #         convert_php_dateformat(settings.SHORT_DATE_FORMAT)
    #     )
    #   return f"{obj.rx.registered_subject.initials} {dob} {obj.rx.registered_subject.gender}"
    #
    # @staticmethod
    # def gender(obj):
    #     return obj.rx.registered_subject.gender
    #
    # @staticmethod
    # def consented(obj):
    #     return obj.rx.registered_subject.consent_datetime.strftime(
    #         convert_php_dateformat(settings.SHORT_DATE_FORMAT)
    #     )
    #
    # @admin.display(description="Subject")
    # def subject_identifier(self, obj=None):
    #     return obj.rx.subject_identifier
