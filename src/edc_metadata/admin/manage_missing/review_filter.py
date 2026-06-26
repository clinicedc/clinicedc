from __future__ import annotations

from django import forms
from django.contrib import admin
from django_audit_fields import ModelAdminAuditFieldsMixin, audit_fieldset_tuple

from edc_model_admin.mixins import TemplatesModelAdminMixin

from ...admin_site import edc_metadata_admin
from ...models import ReviewFilter


class ReviewFilterForm(forms.ModelForm):
    class Meta:
        model = ReviewFilter
        fields = ("name", "user", "query", "shared")


@admin.register(ReviewFilter, site=edc_metadata_admin)
class ReviewFilterAdmin(
    TemplatesModelAdminMixin, ModelAdminAuditFieldsMixin, admin.ModelAdmin
):
    form = ReviewFilterForm
    ordering = ("name",)
    list_display = ("name", "user", "shared", "modified")
    list_filter = ("shared",)
    search_fields = ("name", "user__username")

    fieldsets = (
        [None, {"fields": ("name", "user", "query", "shared")}],
        audit_fieldset_tuple,
    )
