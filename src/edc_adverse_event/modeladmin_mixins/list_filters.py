from django.contrib.admin import SimpleListFilter
from django.db.models import Count, Q
from edc_constants.constants import OTHER
from edc_sites.site import sites


class CauseOfDeathListFilter(SimpleListFilter):
    title = "Cause of death"
    parameter_name = "cause_of_death"

    def lookups(self, request, model_admin):
        values_list = []
        try:
            values_list = (
                model_admin.model.objects.filter(
                    site_id__in=sites.get_site_ids_for_user(request=request)
                )
                .order_by("cause_of_death__name")
                .values_list("cause_of_death__name", "cause_of_death__display_name")
                .annotate(count=Count("cause_of_death__name"))
            )
        except AttributeError:
            values_list = (
                model_admin.model.objects.filter(
                    site_id__in=sites.get_site_ids_for_user(request=request)
                )
                .order_by("cause_of_death")
                .values_list("cause_of_death")
                .annotate(count=Count("cause_of_death"))
            )
        finally:
            try:
                names = [(value[0], value[1]) for value in values_list if value[2] > 0]
            except KeyError:
                names = [(value[0], value[0]) for value in values_list if value[1] > 0]
        if [n[0] for n in names if n[0] == OTHER]:
            values_list = (
                model_admin.model.objects.filter(
                    site_id__in=sites.get_site_ids_for_user(request=request)
                )
                .order_by("cause_of_death_other")
                .values_list("cause_of_death_other")
                .annotate(count=Count("cause_of_death_other"))
            )
            other_names = [
                (f"Other: {value[0]}", f"Other: {value[0]}")
                for value in values_list
                if value[0]
            ]
            names.extend(other_names)
            names = sorted(names)
        return tuple(names)

    def queryset(self, request, queryset):
        if self.value() and self.value() != "none":
            value = self.value().replace("Other: ", "")
            try:
                queryset = queryset.filter(
                    (Q(cause_of_death__name=value) | Q(cause_of_death_other=value)),
                    site_id__in=sites.get_site_ids_for_user(request=request),
                )
            except AttributeError:
                queryset = queryset.filter(
                    site_id__in=sites.get_site_ids_for_user(request=request),
                    cause_of_death=value,
                )
        return queryset
