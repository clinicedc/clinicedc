from typing import Tuple

from django import forms
from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from ...admin_site import edc_pharmacy_admin
from ...models import Assignment
from ..model_admin_mixin import ModelAdminMixin


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = "__all__"


@admin.register(Assignment, site=edc_pharmacy_admin)
class AssignmentAdmin(ModelAdminMixin, admin.ModelAdmin):
    show_object_tools = True
    show_cancel = True

    form = AssignmentForm

    fieldsets = (
        (
            None,
            {"fields": ["name", "display_name"]},
        ),
        audit_fieldset_tuple,
    )

    list_display: Tuple[str, ...] = (
        "name",
        "display_name",
        "created",
        "modified",
    )

    search_fields: Tuple[str, ...] = ("name", "display_name")

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ("name",)
        return self.readonly_fields
