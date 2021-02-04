from django.contrib import admin
from edc_constants.constants import NO

from ..custom_label_condition import CustomLabelCondition
from ..form_label import FormLabel
from ..form_label_modeladmin_mixin import FormLabelModelAdminMixin
from .models import MyModel

VISIT_ONE = "1000"
VISIT_TWO = "2000"


class MyCustomLabelCondition(CustomLabelCondition):
    def check(self, **kwargs):
        if self.previous_obj:
            return self.previous_obj.circumcised == NO
        return False


class MyModelAdmin(FormLabelModelAdminMixin, admin.ModelAdmin):
    """Demonstrate use of a custom form label."""

    fieldsets = (
        (
            "Not special fields",
            {"fields": ("subject_visit", "report_datetime", "circumcised")},
        ),
    )

    custom_form_labels = [
        FormLabel(
            field="circumcised",
            custom_label="Since we last saw you in {previous_visit}, were you circumcised?",
            condition_cls=MyCustomLabelCondition,
        )
    ]


admin.site.register(MyModel, MyModelAdmin)
