from decimal import Decimal

from django.contrib.admin import SimpleListFilter

__all__ = ["FbgListFilter", "OgttListFilter"]


class FbgListFilter(SimpleListFilter):
    title = "FBG"
    parameter_name = "fbg_value"

    def lookups(self, request, model_admin):
        return (
            ("fbg_normal", "below 7.0 mmol/L"),
            ("fbg_high", "above 7.0 mmol/L (incl)"),
        )

    def queryset(self, request, queryset):
        self.value()
        if self.value() == "fbg_normal":
            return queryset.filter(fbg_value__lt=Decimal("7.0"))
        if self.value() == "fbg_high":
            return queryset.filter(fbg_value__gte=Decimal("7.0"))
        return queryset


class OgttListFilter(SimpleListFilter):
    title = "OGTT"
    parameter_name = "ogtt_value"

    def lookups(self, request, model_admin):
        return (
            ("ogtt_normal", "below 11.1 mmol/L"),
            ("ogtt_high", "above 11.1 mmol/L (incl)"),
        )

    def queryset(self, request, queryset):
        if self.value() == "ogtt_normal":
            return queryset.filter(ogtt_value__lt=Decimal("11.1"))
        if self.value() == "ogtt_high":
            return queryset.filter(ogtt_value__gte=Decimal("11.1"))
        return queryset
