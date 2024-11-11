from django.contrib.admin import SimpleListFilter
from django.contrib.sites.shortcuts import get_current_site
from edc_constants.choices import YES_NO
from edc_constants.constants import NO

from ..models import Medication, Rx, Stock


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


class AllocationListFilter(SimpleListFilter):
    title = "Allocated"
    parameter_name = "allocated"

    def lookups(self, request, model_admin):
        return YES_NO

    def queryset(self, request, queryset):
        qs = None
        if self.value():
            isnull = True if self.value() == NO else False
            qs = Stock.objects.filter(allocation__isnull=isnull)
        return qs


class HasOrderNumFilter(SimpleListFilter):
    title = "Has Order #"
    parameter_name = "has_order_num"

    def lookups(self, request, model_admin):
        return YES_NO

    def queryset(self, request, queryset):
        qs = None
        if self.value():
            isnull = True if self.value() == NO else False
            qs = Stock.objects.filter(receive_item__order_item__order__isnull=isnull)
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
            qs = Stock.objects.filter(receive_item__receive__isnull=isnull)
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
            qs = Stock.objects.filter(repack_request__isnull=isnull)
        return qs
