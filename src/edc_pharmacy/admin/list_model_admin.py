from django.contrib import admin
from edc_list_data.admin import ListModelAdminMixin

from ..admin_site import edc_pharmacy_admin
from ..models import Container, FormulationType, FrequencyUnits, Route, Units


@admin.register(Container, site=edc_pharmacy_admin)
class ContainerAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(FormulationType, site=edc_pharmacy_admin)
class FormulationTypeAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(FrequencyUnits, site=edc_pharmacy_admin)
class FrequencyUnitsAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(Route, site=edc_pharmacy_admin)
class RouteAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(Units, site=edc_pharmacy_admin)
class UnitsAdmin(ListModelAdminMixin, admin.ModelAdmin):
    pass
