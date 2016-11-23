from django.contrib import admin

from .admin_site import edc_lab_admin
from .models import Aliquot, SpecimenCollection, SpecimenCollectionItem
from .modeladmin_mixins import (
    AliquotModelAdminMixin, SpecimenCollectionModelAdminMixin, SpecimenCollectionItemModelAdminMixin)


@admin.register(Aliquot, site=edc_lab_admin)
class AliquotAdmin(AliquotModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(SpecimenCollectionItem, site=edc_lab_admin)
class SpecimenCollectionItemAdmin(SpecimenCollectionItemModelAdminMixin, admin.ModelAdmin):
    pass


@admin.register(SpecimenCollection, site=edc_lab_admin)
class SpecimenCollectionAdmin(SpecimenCollectionModelAdminMixin, admin.ModelAdmin):
    pass
