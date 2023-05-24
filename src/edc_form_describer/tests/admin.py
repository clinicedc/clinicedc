from django.contrib import admin
from django.contrib.admin import register
from django_audit_fields import audit_fieldset_tuple
from edc_model_admin.mixins import ModelAdminFormInstructionsMixin

from .forms import MyForm
from .models import MyModel


@register(MyModel)
class MyModelAdmin(ModelAdminFormInstructionsMixin, admin.ModelAdmin):
    form = MyForm

    fieldsets = (
        (
            "Not special fields",
            {"fields": ("subject_visit", "report_datetime", "f1", "f2", "f3")},
        ),
        (
            "Visit Two Additional Questions",
            {"fields": ("f4", "f5")},
        ),
        (
            "Summary",
            {"fields": ("summary_one", "summary_two")},
        ),
        audit_fieldset_tuple,
    )
