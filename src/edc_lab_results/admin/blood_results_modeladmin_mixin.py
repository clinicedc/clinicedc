from django.contrib import admin
from django.contrib.admin import ModelAdmin
from edc_action_item import action_fields


class BloodResultsModelAdminMixin(ModelAdmin):

    form = None

    fieldsets = None

    autocomplete_fields = ["requisition"]

    radio_fields = {
        "results_abnormal": admin.VERTICAL,
        "results_reportable": admin.VERTICAL,
    }

    list_display = ("missing_count", "missing", "abnormal", "reportable", "action_identifier")

    search_fields = (
        "action_identifier",
        "subject_visit__subject_identifier",
        "tracking_identifier",
    )

    # TODO: add filter to see below grade 3,4
    def get_list_filter(self, request) -> tuple:
        list_filter = super().get_list_filter(request)
        list_filter = ("missing_count", "results_abnormal", "results_reportable") + list_filter
        return list_filter

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "appointment" and request.GET.get("appointment"):
            kwargs["queryset"] = db_field.related_model.objects.filter(
                pk=request.GET.get("appointment", 0)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None) -> tuple:
        readonly_fields = super().get_readonly_fields(request, obj=obj)  # type: ignore
        readonly_fields += ("summary",) + action_fields
        readonly_fields = set(list(readonly_fields))
        return tuple(readonly_fields)
