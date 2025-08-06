from django.contrib.admin import SimpleListFilter
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Count, F, Q
from django.utils.translation import gettext as _
from edc_constants.choices import YES_NO, YES_NO_NA
from edc_constants.constants import NEW, NO, NOT_APPLICABLE, PARTIAL, RECEIVED, YES

from ..models import Medication, Rx
from ..utils import blinded_user


class MedicationsListFilter(SimpleListFilter):
    title = "Medication"
    parameter_name = "medication_name"

    def lookups(self, request, model_admin):
        medications = []
        for medication in Medication.objects.all().order_by("name"):
            medications.append((medication.name, medication.name.replace("_", " ").title()))
        medications.append(("none", "None"))
        return tuple(medications)

    def queryset(self, request, queryset):
        """Returns a queryset if the Medication name is in the list of sites"""
        qs = None
        if self.value():
            if self.value() == "none":
                qs = Rx.objects.filter(
                    medications__isnull=True, site=get_current_site(request)
                )
            else:
                qs = Rx.objects.filter(
                    medications__name__in=[self.value()], site=get_current_site(request)
                )
        return qs


class ConfirmedListFilter(SimpleListFilter):
    title = "Confirmed"
    parameter_name = "confirmation"

    def lookups(self, request, model_admin):
        return YES_NO

    def queryset(self, request, queryset):
        qs = None
        if self.value():
            if self.value() == YES:
                qs = queryset.filter(confirmation__isnull=False)
            elif self.value() == NO:
                qs = queryset.filter(confirmation__isnull=True)
        return qs


class AllocationListFilter(SimpleListFilter):
    title = "Allocated"
    parameter_name = "allocated"

    def lookups(self, request, model_admin):
        return YES_NO_NA

    def queryset(self, request, queryset):
        qs = None
        if self.value():
            if self.value() == YES:
                qs = queryset.filter(
                    from_stock__isnull=False,
                    allocation__isnull=False,
                    container__may_request_as=True,
                )
            elif self.value() == NO:
                qs = queryset.filter(
                    from_stock__isnull=False,
                    allocation__isnull=True,
                    container__may_request_as=True,
                )
            elif self.value() == NOT_APPLICABLE:
                qs = queryset.filter(
                    from_stock__isnull=True,
                    allocation__isnull=True,
                    container__may_request_as=False,
                )
        return qs


class StockItemAllocationListFilter(SimpleListFilter):
    title = "Allocated"
    parameter_name = "allocated"

    def lookups(self, request, model_admin):
        return YES_NO

    def queryset(self, request, queryset):
        qs = None
        if self.value():
            if self.value() == YES:
                qs = queryset.filter(allocation__isnull=False)
            elif self.value() == NO:
                qs = queryset.filter(allocation__isnull=True)
        return qs


class StockItemTransferredListFilter(SimpleListFilter):
    title = "Transferred"
    parameter_name = "transferred"

    def lookups(self, request, model_admin):
        return YES_NO

    def queryset(self, request, queryset):
        qs = None
        if self.value():
            if self.value() == YES:
                qs = queryset.filter(
                    allocation__isnull=False,
                    allocation__stock__stocktransferitem__isnull=False,
                )
            elif self.value() == NO:
                qs = queryset.filter(
                    allocation__isnull=True,
                    allocation__stock__stocktransferitem__isnull=True,
                )
        return qs


class TransferredListFilter(SimpleListFilter):
    title = "Transferred"
    parameter_name = "transferred"

    def lookups(self, request, model_admin):
        return YES_NO_NA

    def queryset(self, request, queryset):
        qs = None
        if self.value():
            if self.value() == YES:
                qs = queryset.filter(
                    container__may_request_as=True,
                    allocation__stock_request_item__stock_request__location=F("location"),
                )
            elif self.value() == NO:
                qs = queryset.filter(
                    ~Q(allocation__stock_request_item__stock_request__location=F("location")),
                    container__may_request_as=True,
                )
            elif self.value() == NOT_APPLICABLE:
                qs = queryset.filter(allocation__isnull=True, container__may_request_as=False)
        return qs


class AssignmentListFilter(SimpleListFilter):
    title = "Assignment"
    parameter_name = "assignment"
    lookup_str = "assignment__name"

    def lookups(self, request, model_admin):
        groupby = model_admin.model.objects.values(self.lookup_str).annotate(
            count=Count(self.lookup_str)
        )
        if not blinded_user(request):
            choices = []
            for name in [ann.get(self.lookup_str) for ann in groupby]:
                choices.append((name, name or "None"))
            return tuple(choices)
        return ("****", "****"), ("****", "****")

    def queryset(self, request, queryset):
        qs = None
        if self.value():
            qs = queryset.filter(**{self.lookup_str: self.value()})
        return qs


class ProductAssignmentListFilter(AssignmentListFilter):
    title = "Assignment"
    parameter_name = "product_assignment"
    lookup_str = "product__assignment__name"


class HasOrderNumFilter(SimpleListFilter):
    title = "Has Order #"
    parameter_name = "has_order_num"

    def lookups(self, request, model_admin):
        return YES_NO

    def queryset(self, request, queryset):
        qs = None
        if self.value():
            isnull = True if self.value() == NO else False
            qs = queryset.filter(receive_item__order_item__order__isnull=isnull)
        return qs


class HasReceiveNumFilter(SimpleListFilter):
    title = "Has Receive #"
    parameter_name = "has_receive_num"

    def lookups(self, request, model_admin):
        return YES_NO

    def queryset(self, request, queryset):
        qs = None
        if self.value():
            isnull = True if self.value() == NO else False
            qs = queryset.filter(receive_item__receive__isnull=isnull)
        return qs


class HasRepackNumFilter(SimpleListFilter):
    title = "Has Repack #"
    parameter_name = "has_repack_num"

    def lookups(self, request, model_admin):
        return YES_NO

    def queryset(self, request, queryset):
        qs = None
        if self.value():
            isnull = True if self.value() == NO else False
            qs = queryset.filter(repack_request__isnull=isnull)
        return qs


class TransferredFilter(SimpleListFilter):
    title = "Transferred to site"
    parameter_name = "transferred"

    def lookups(self, request, model_admin):
        return (YES, YES), (NO, NO)

    def queryset(self, request, queryset):
        qs = None
        if self.value():
            opts = dict(
                from_stock__isnull=False,
                confirmation__isnull=False,
                allocation__isnull=False,
            )
            if self.value() == YES:
                qs = queryset.filter(stocktransferitem__isnull=False, **opts)
            elif self.value() == NO:
                qs = queryset.filter(stocktransferitem__isnull=True, **opts)
        return qs


class ConfirmedAtSiteFilter(SimpleListFilter):
    title = "Confirmed at site"
    parameter_name = "confirmed_at_site"

    def lookups(self, request, model_admin):
        return (YES, YES), (NO, NO)

    def queryset(self, request, queryset):
        qs = None
        if self.value():
            opts = dict(
                from_stock__isnull=False,
                confirmation__isnull=False,
                allocation__isnull=False,
                stocktransferitem__isnull=False,
            )
            if self.value() == YES:
                qs = queryset.filter(confirmationatsiteitem__isnull=False, **opts)
            elif self.value() == NO:
                qs = queryset.filter(confirmationatsiteitem__isnull=True, **opts)
        return qs


class StoredAtSiteFilter(SimpleListFilter):
    title = "Stored at site"
    parameter_name = "stored_at_site_now"

    def lookups(self, request, model_admin):
        return YES_NO_NA

    def queryset(self, request, queryset):
        qs = None
        if self.value():
            if self.value() == YES:
                qs = queryset.filter(
                    from_stock__isnull=False,
                    confirmation__isnull=False,
                    allocation__isnull=False,
                    stocktransferitem__isnull=False,
                    confirmationatsiteitem__isnull=False,
                    storagebinitem__isnull=False,
                    dispenseitem__isnull=True,
                )
            elif self.value() == NO:
                qs = queryset.filter(
                    from_stock__isnull=False,
                    confirmation__isnull=False,
                    allocation__isnull=False,
                    stocktransferitem__isnull=False,
                    confirmationatsiteitem__isnull=False,
                    storagebinitem__isnull=True,
                    dispenseitem__isnull=True,
                )
            elif self.value() == NOT_APPLICABLE:
                qs = queryset.filter(
                    from_stock__isnull=False,
                    confirmation__isnull=False,
                    allocation__isnull=False,
                    stocktransferitem__isnull=False,
                    confirmationatsiteitem__isnull=False,
                    storagebinitem__isnull=True,
                    dispenseitem__isnull=False,
                )
        return qs


class DispensedFilter(SimpleListFilter):
    title = "Dispensed"
    parameter_name = "dispensed"

    def lookups(self, request, model_admin):
        return YES_NO

    def queryset(self, request, queryset):
        qs = None
        if self.value():
            opts = dict(
                from_stock__isnull=False,
                confirmation__isnull=False,
                allocation__isnull=False,
                stocktransferitem__isnull=False,
                confirmationatsiteitem__isnull=False,
            )
            if self.value() == YES:
                qs = queryset.filter(dispenseitem__isnull=False, **opts)
            elif self.value() == NO:
                qs = queryset.filter(dispenseitem__isnull=True, **opts)
        return qs


class HasCodesListFilter(SimpleListFilter):
    title = "Has codes"
    parameter_name = "has_codes"

    def lookups(self, request, model_admin):
        return (YES, YES), (NO, NO)

    def queryset(self, request, queryset):
        qs = None
        if self.value():
            if self.value() == YES:
                qs = queryset.filter(codes__isnull=False)
            elif self.value() == NO:
                qs = queryset.filter(codes__isnull=True)
        return qs


class StockRequestItemPendingListFilter(SimpleListFilter):
    title = "Request Status"
    parameter_name = "item_status"

    def lookups(self, request, model_admin):
        return (
            ("not_allocated", "Not allocated"),
            ("allocated_only", "Allocated only"),
            ("transferred", "Allocation and transferred"),
        )

    def queryset(self, request, queryset):
        qs = None
        if self.value():
            if self.value() == "not_allocated":
                qs = queryset.filter(allocation__isnull=True)
            elif self.value() == "allocated_only":
                qs = queryset.filter(
                    Q(allocation__isnull=False)
                    & Q(allocation__stock__stocktransferitem__isnull=True)
                    & ~Q(allocation__stock__location=F("stock_request__location"))
                )
            elif self.value() == "transferred":
                qs = queryset.filter(
                    Q(allocation__isnull=False)
                    & Q(allocation__stock__stocktransferitem__isnull=False)
                    & Q(allocation__stock__location=F("stock_request__location"))
                )
        return qs


class OrderItemStatusListFilter(SimpleListFilter):
    title = "Status"
    parameter_name = "order_item_status"

    def lookups(self, request, model_admin):
        return (
            (NEW, _("New")),
            (PARTIAL, _("Partial")),
            (RECEIVED, _("Received")),
        )

    def queryset(self, request, queryset):
        qs = None
        if self.value():
            if self.value() == RECEIVED:
                qs = queryset.filter(unit_qty=0)
            elif self.value() == PARTIAL:
                qs = queryset.filter(Q(unit_qty_ordered__gt=F("unit_qty")) & ~Q(unit_qty=0))
            elif self.value() == NEW:
                qs = queryset.filter(unit_qty=F("unit_qty_ordered"))
        return qs


class DecantedListFilter(SimpleListFilter):
    title = "Decanted"
    parameter_name = "decanted"

    def lookups(self, request, model_admin):
        return YES_NO

    def queryset(self, request, queryset):
        qs = None
        if self.value():
            if self.value() == YES:
                qs = queryset.filter(from_stock__isnull=False)
            elif self.value() == NO:
                qs = queryset.filter(from_stock__isnull=True)
        return qs


class StorageBinItemDispensedFilter(SimpleListFilter):
    title = "Dispensed"
    parameter_name = "dispensed"

    def lookups(self, request, model_admin):
        return (YES, YES), (NO, NO)

    def queryset(self, request, queryset):
        qs = None
        if self.value():
            if self.value() == YES:
                qs = queryset.filter(
                    stock__dispenseitem__isnull=False,
                )
            elif self.value() == NO:
                qs = queryset.filter(
                    stock__dispenseitem__isnull=True,
                )
        return qs
