from django.contrib.admin import ModelAdmin
from django.contrib.admin.decorators import register
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin
from edc_model_admin.mixins import (
    ModelAdminFormInstructionsMixin,
    ModelAdminInstitutionMixin,
    TemplatesModelAdminMixin,
)
from edc_registration.admin import RegisteredSubjectAdmin as BaseRegisteredSubjectAdmin

from ..admin_site import edc_pharmacy_admin
from ..models import (
    LabelSpecificationProxy,
    RegisteredSubjectProxy,
    SiteProxy,
    VisitSchedule,
)


@register(RegisteredSubjectProxy, site=edc_pharmacy_admin)
class RegisteredSubjectProxyAdmin(BaseRegisteredSubjectAdmin):
    ordering = ("subject_identifier",)
    search_fields = ("subject_identifier",)


@register(VisitSchedule, site=edc_pharmacy_admin)
class VisitScheduleAdmin(ModelAdmin):
    ordering = ("visit_schedule_name", "schedule_name", "visit_code")
    search_fields = ("visit_code", "visit_title")


@register(LabelSpecificationProxy, site=edc_pharmacy_admin)
class LabelSpecificationProxyAdmin(
    TemplatesModelAdminMixin,
    ModelAdminFormInstructionsMixin,
    ModelAdminRevisionMixin,
    ModelAdminInstitutionMixin,
    ModelAdmin,
):
    show_object_tools = True
    ordering = ("name",)
    list_display = ["name", "page_description", "layout_description", "label_description"]
    search_fields = ["id", "name"]


@register(SiteProxy, site=edc_pharmacy_admin)
class SiteProxyAdmin(ModelAdmin):
    ordering = ("name",)
    search_fields = ["id", "name"]
