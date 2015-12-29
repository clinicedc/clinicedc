from django.contrib import admin
from edc_base.modeladmin.admin import BaseModelAdmin
from .actions import toggle_active, toggle_scale, toggle_lln, toggle_uln, toggle_serum
from .models import GradingList, GradingListItem, ReferenceRangeList, ReferenceRangeListItem
from .forms import GradingListItemForm


class GradingListAdmin(BaseModelAdmin):
    pass
admin.site.register(GradingList, GradingListAdmin)


class GradingListItemAdmin(BaseModelAdmin):

    form = GradingListItemForm

    fields = (
        "test_code",
        "grading_list",
        "grade",
        "fasting",
        "serum",
        "active",
        "dummy",
        "scale",
        "gender",
        "hiv_status",
        "value_unit",
        "use_uln",
        "use_lln",
        "value_low_quantifier",
        "value_low",
        "value_low_calc",
        "value_high_quantifier",
        "value_high",
        "value_high_calc",
        "age_low",
        "age_low_unit",
        "age_low_quantifier",
        "age_high",
        "age_high_unit",
        "age_high_quantifier",
        "comment",
        "import_datetime",
    )

    radio_fields = {
        "scale": admin.VERTICAL,
        "gender": admin.VERTICAL,
        "hiv_status": admin.VERTICAL,
        "fasting": admin.VERTICAL,
        "value_low_calc": admin.VERTICAL,
        "value_high_calc": admin.VERTICAL,
        "serum": admin.VERTICAL}

    list_display = ('test_code', 'grade', 'active', 'describe', 'hiv_status', 'gender', 'value_low', 'value_high', 'value_unit', 'age_low', 'age_low_unit', 'age_low_quantifier',
                    'age_high', 'age_high_unit', 'age_high_quantifier', 'grading_list', 'scale', 'use_lln', 'use_uln', 'serum', 'fasting')
    search_fields = ['grade', 'test_code__code', 'test_code__name', 'value_low', 'value_high', 'hiv_status']
    list_filter = ('grade', 'hiv_status', 'grading_list', 'scale', 'active', 'use_lln', 'use_uln', 'serum', 'fasting', 'value_unit', 'test_code')
    actions = [toggle_active, toggle_scale, toggle_lln, toggle_uln, toggle_serum]
admin.site.register(GradingListItem, GradingListItemAdmin)


class ReferenceRangeListAdmin(BaseModelAdmin):
    pass
admin.site.register(ReferenceRangeList, ReferenceRangeListAdmin)


class ReferenceRangeListItemAdmin(BaseModelAdmin):
    list_display = ('test_code', 'active', 'describe', 'gender', 'value_low', 'value_high', 'age_low', 'age_low_unit', 'age_low_quantifier',
                    'age_high', 'age_high_unit', 'age_high_quantifier', 'reference_range_list', 'scale')
    search_fields = ['test_code__code', 'test_code__name', 'value_low', 'value_high']
    list_filter = ('hiv_status', 'reference_range_list', 'scale', 'active', 'test_code')
    actions = [toggle_active, toggle_scale]
admin.site.register(ReferenceRangeListItem, ReferenceRangeListItemAdmin)
