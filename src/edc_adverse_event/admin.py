from django.contrib import admin

from edc_list_data.admin import ListModelAdminMixin

from .admin_site import edc_adverse_event_admin
from .models import AeClassification, CauseOfDeath, SaeReason


@admin.register(AeClassification, site=edc_adverse_event_admin)
class AeClassificationAdmin(ListModelAdminMixin, admin.ModelAdmin):
    change_list_template = "edc_adverse_event/admin/change_list.html"
    change_form_template = "edc_adverse_event/admin/change_form.html"


@admin.register(CauseOfDeath, site=edc_adverse_event_admin)
class CauseOfDeathAdmin(ListModelAdminMixin, admin.ModelAdmin):
    change_list_template = "edc_adverse_event/admin/change_list.html"
    change_form_template = "edc_adverse_event/admin/change_form.html"


@admin.register(SaeReason, site=edc_adverse_event_admin)
class SaeReasonAdmin(ListModelAdminMixin, admin.ModelAdmin):
    change_list_template = "edc_adverse_event/admin/change_list.html"
    change_form_template = "edc_adverse_event/admin/change_form.html"
