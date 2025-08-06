from django.contrib import admin
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin

from edc_model_admin.mixins import (
    ModelAdminFormAutoNumberMixin,
    ModelAdminFormInstructionsMixin,
    ModelAdminInstitutionMixin,
    ModelAdminNextUrlRedirectMixin,
    ModelAdminRedirectOnDeleteMixin,
    TemplatesModelAdminMixin,
)

from ..actions import print_test_label_sheet_action
from ..admin_site import edc_pylabels_admin
from ..forms import LabelConfigurationForm
from ..models import LabelConfiguration
from ..site_label_configs import site_label_configs


@admin.register(LabelConfiguration, site=edc_pylabels_admin)
class LabelConfigurationAdmin(
    TemplatesModelAdminMixin,
    ModelAdminNextUrlRedirectMixin,  # add
    ModelAdminFormInstructionsMixin,  # add
    ModelAdminFormAutoNumberMixin,
    ModelAdminRevisionMixin,  # add
    ModelAdminInstitutionMixin,  # add
    ModelAdminRedirectOnDeleteMixin,
    admin.ModelAdmin,
):
    show_object_tools = True
    actions = [print_test_label_sheet_action]
    form = LabelConfigurationForm

    instructions = (
        "This model links the label specification with a registered label configuration."
    )

    date_hierarchy = "created"

    fieldsets = ((None, {"fields": ("name", "label_specification", "requires_allocation")}),)

    list_display = ("name", "label_specification")

    list_filter = ("label_specification",)

    search_fields = ("name", "label_specification__name")

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "name":
            kwargs["choices"] = [(k, k) for k in site_label_configs.all()]
        return super().formfield_for_choice_field(db_field, request, **kwargs)
