from django.contrib import admin
from django_pylabels.actions import copy_label_specification, export_to_csv
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin

from edc_model_admin.mixins import (
    ModelAdminFormAutoNumberMixin,
    ModelAdminFormInstructionsMixin,
    ModelAdminInstitutionMixin,
    ModelAdminNextUrlRedirectMixin,
    ModelAdminRedirectOnDeleteMixin,
    TemplatesModelAdminMixin,
)

from ..admin_site import edc_pylabels_admin
from ..models import LabelSpecification


@admin.register(LabelSpecification, site=edc_pylabels_admin)
class LabelSpecificationAdmin(
    TemplatesModelAdminMixin,
    ModelAdminNextUrlRedirectMixin,  # add
    ModelAdminFormInstructionsMixin,  # add
    ModelAdminFormAutoNumberMixin,
    ModelAdminRevisionMixin,  # add
    ModelAdminInstitutionMixin,  # add
    ModelAdminRedirectOnDeleteMixin,
    admin.ModelAdmin,
):
    actions = [copy_label_specification, export_to_csv]

    instructions = (
        "This model captures the dimensions, rows, columns, "
        "and spacing for label sheet stationery."
    )

    date_hierarchy = "created"

    list_display = (
        "name",
        "page_description",
        "layout_description",
        "label_description",
        "border",
    )

    readonly_fields = (
        "page_description",
        "layout_description",
        "label_description",
    )

    list_filter = ("created", "modified")
