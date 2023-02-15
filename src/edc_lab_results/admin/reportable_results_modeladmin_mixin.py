from django.contrib import admin
from django.contrib.admin import ModelAdmin
from edc_action_item import ActionItemModelAdminMixin


class ReportableResultsModelAdminMixin(ActionItemModelAdminMixin, ModelAdmin):
    form = None

    fieldsets = None

    autocomplete_fields = ["requisition"]

    radio_fields = {
        "results_abnormal": admin.VERTICAL,
        "results_reportable": admin.VERTICAL,
    }

    # TODO: add filter to see below grade 3,4
    def get_list_filter(self, request) -> tuple:
        fields = super().get_list_filter(request)
        custom_fields = ("missing_count", "results_abnormal", "results_reportable")
        return tuple(f for f in custom_fields if f not in fields) + fields

    def get_list_display(self, request):
        fields = super().get_list_display(request)
        fields = list(fields)
        custom_fields = [
            "missing_count",
            "missing",
            "abnormal",
            "reportable",
            "action_identifier",
        ]
        fields[4:1] = custom_fields
        return fields

    def get_readonly_fields(self, request, obj=None) -> tuple:
        fields = super().get_readonly_fields(request, obj=obj)
        custom_fields = ("summary",)
        return tuple(set(fields + custom_fields))

    def get_search_fields(self, request):
        fields = super().get_search_fields(request)
        fields = list(fields)
        fields.insert(0, "subject_visit__subject_identifier")
        return tuple(set(fields))

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "appointment" and request.GET.get("appointment"):
            kwargs["queryset"] = db_field.related_model.objects.filter(
                pk=request.GET.get("appointment", 0)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
