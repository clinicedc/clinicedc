from django.contrib import admin
from edc_constants.constants import NO

from edc_fieldsets.fieldset import Fieldset
from edc_fieldsets.fieldsets_modeladmin_mixin import FieldsetsModelAdminMixin
from .models import MyModel
from ..form_label import FormLabel
from ..custom_label_condition import CustomLabelCondition

VISIT_ONE = '1000'
VISIT_TWO = '2000'

visit_two_fieldset = Fieldset(
    'f4',
    'f5',
    section='Visit Two Additional Questions')


summary_fieldset = Fieldset(
    'summary_one',
    'summary_two',
    section='Summary')


class MyCustomLabelCondition(CustomLabelCondition):
    def check(self, **kwargs):
        if self.previous_obj.f1 == NO:
            return True
        return False


class MyModelAdmin(FieldsetsModelAdminMixin, admin.ModelAdmin):
    """Demonstrate use of a custom form label.

    """

    fieldsets = (
        ('Not special fields', {
            'fields': (
                'subject_visit',
                'report_datetime',
                'f1',
                'f2',
                'f3')},
         ),
    )

    custom_form_labels = [
        FormLabel(
            field='f1',
            custom_label='Since we last saw you in {previous_visit}, were you circumcised?',
            condition_cls=MyCustomLabelCondition)
    ]


admin.site.register(MyModel, MyModelAdmin)
