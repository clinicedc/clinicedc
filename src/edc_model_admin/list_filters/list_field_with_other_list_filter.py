from __future__ import annotations

from django.contrib.admin import SimpleListFilter
from django.core.exceptions import FieldError
from django.db.models import Count, Q

from edc_constants.constants import OTHER
from edc_sites.site import sites


class ListFieldWithOtherListFilter(SimpleListFilter):
    title: str
    parameter_name: str
    other_parameter_name: str

    def lookups(self, request, model_admin):
        values_list = []
        try:
            values_list = (
                model_admin.model.objects.filter(
                    site_id__in=sites.get_site_ids_for_user(request=request)
                )
                .order_by(f"{self.parameter_name}__name")
                .values_list(
                    f"{self.parameter_name}__name",
                    f"{self.parameter_name}__display_name",
                )
                .annotate(count=Count(f"{self.parameter_name}__name"))
            )
        except (AttributeError, FieldError):
            values_list = (
                model_admin.model.objects.filter(
                    site_id__in=sites.get_site_ids_for_user(request=request)
                )
                .order_by(self.parameter_name)
                .values_list(self.parameter_name)
                .annotate(count=Count(self.parameter_name))
            )
        finally:
            try:
                names = [(value[0], value[1]) for value in values_list if value[2] > 0]
            except IndexError:
                names = [(value[0], value[0]) for value in values_list if value[1] > 0]
        if [n[0] for n in names if n[0] == OTHER]:
            values_list = (
                model_admin.model.objects.filter(
                    site_id__in=sites.get_site_ids_for_user(request=request)
                )
                .order_by(self.other_parameter_name)
                .values_list(self.other_parameter_name)
                .annotate(count=Count(self.other_parameter_name))
            )
            other_names = [
                (f"Other: {value[0]}", f"Other: {value[0].capitalize()[:25]}")
                for value in values_list
                if value[0]
            ]
            names = sorted(names)
            other_names = sorted(other_names)
            names.extend(other_names)
        return tuple(names)

    def queryset(self, request, queryset):
        if self.value() and self.value() != "none":
            value = self.value().replace("Other: ", "")
            try:
                queryset = queryset.filter(
                    (
                        Q(**{f"{self.parameter_name}__name": value})
                        | Q(**{self.other_parameter_name: value})
                    ),
                    site_id__in=sites.get_site_ids_for_user(request=request),
                )
            except AttributeError:
                opts = {
                    "site_id__in": sites.get_site_ids_for_user(request=request),
                    self.parameter_name: value,
                }
                queryset = queryset.filter(**opts)
        return queryset
