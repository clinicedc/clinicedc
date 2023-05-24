from django.contrib.admin import SimpleListFilter
from django.contrib.sites.shortcuts import get_current_site

from ..models import Medication, Rx


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
