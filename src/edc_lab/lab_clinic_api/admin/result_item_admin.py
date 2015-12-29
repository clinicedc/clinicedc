from django.contrib import admin
from collections import OrderedDict

from edc_base.modeladmin.admin import BaseModelAdmin
from edc.export.actions import export_as_csv_action

from ..actions import recalculate_grading
from ..forms import ResultItemForm
from ..models import ResultItem


class ResultItemAdmin(BaseModelAdmin):

    def __init__(self, *args, **kwargs):
        super(ResultItemAdmin, self).__init__(*args, **kwargs)
    date_hierarchy = 'result_item_datetime'
    form = ResultItemForm
    list_display = (
        "test_code",
        "result",
        "subject_identifier",
        'subject_type',
        "result_item_value",
        "result_item_value_as_float",
        "result_item_datetime",
        "to_result",
        "grade_range",
        "grade_flag",
        "reference_range",
        "reference_flag",
        'validation_status',
        'import_datetime')
    list_filter = ('grade_flag', 'reference_flag', "validation_status", 'subject_type', "result_item_datetime", 'import_datetime', "test_code")
    search_fields = ('id', 'test_code__code',
                     'result__result_identifier',
                     "subject_identifier",
                     "receive_identifier",
                     "result_item_value")
    radio_fields = {
        "result_item_quantifier": admin.VERTICAL,
        "validation_status": admin.VERTICAL}
    actions = [
        export_as_csv_action("CSV Export: adds subject_identifier, gender, dob",
            fields=[],
            delimiter=',',
            exclude=['id', 'revision', 'hostname_created', 'hostname_modified', 'user_created','user_modified'],
            extra_fields=OrderedDict(
                {'gender': 'result__order__aliquot__receive__registered_subject__gender',
                'dob': 'result__order__aliquot__receive__registered_subject__dob'}),
                ),
        recalculate_grading,]
    list_per_page = 35

    def get_readonly_fields(self, request, obj):
        return [field.name for field in obj._meta.fields if field.editable]

admin.site.register(ResultItem, ResultItemAdmin)
