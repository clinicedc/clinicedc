from django.contrib import admin
from django_audit_fields.admin import audit_fieldset_tuple

from ..fieldset import Fieldset
from ..fieldsets_modeladmin_mixin import FieldsetsModelAdminMixin
from .models import MyModel, MyModel2

VISIT_ONE = "1000"
VISIT_TWO = "2000"

visit_two_fieldset = Fieldset("f4", "f5", section="Visit Two Additional Questions")


summary_fieldset = Fieldset("summary_one", "summary_two", section="Summary")


class MyModelAdmin(FieldsetsModelAdminMixin, admin.ModelAdmin):

    """Demonstrate the use of conditional_fieldsets.

    Fieldset "visit_two_fieldset" will only show on the admin
    form if the visit_code is '2000'
    """

    conditional_fieldsets = {VISIT_TWO: (visit_two_fieldset,)}

    fieldsets = (
        (
            "Not special fields",
            {"fields": ("subject_visit", "report_datetime", "f1", "f2", "f3")},
        ),
        audit_fieldset_tuple,
    )


admin.site.register(MyModel, MyModelAdmin)


class MyModel2Admin(FieldsetsModelAdminMixin, admin.ModelAdmin):
    """Demonstrate that the fieldsets listed in  fieldsets_move_to_end
    will always be last even after a conditional fieldset
    is inserted.

    """

    fieldsets_move_to_end = ["Summary", audit_fieldset_tuple[0]]

    conditional_fieldsets = {VISIT_TWO: (visit_two_fieldset,)}

    fieldsets = (
        (
            "Not special fields",
            {"fields": ("subject_visit", "report_datetime", "f1", "f2", "f3")},
        ),
        summary_fieldset.fieldset,
        audit_fieldset_tuple,
    )


admin.site.register(MyModel2, MyModel2Admin)
