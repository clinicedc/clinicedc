from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import UUID_PATTERN

from .fieldsets import Fieldsets


class FieldsetsModelAdminMixin:

    """A class that helps modify fieldsets for subject models

    * Model is expected to have a relation to have subject_visit__appointment.
    * Expects appointment to be in GET
    """

    appointment_model: str = "edc_appointment.appointment"
    # key: value where key is a visit_code. value is a fieldlist object
    conditional_fieldlists: dict = {}
    # key: value where key is a visit code. value is a fieldsets object.
    conditional_fieldsets: dict = {}

    fieldsets_move_to_end = None

    def get_key(self, request=None, **kwargs) -> str:
        """Returns a string that is the key to `get` the
        value in the "conditional" dictionaries.

        For example:
            appointment.visit_code == '1000' will be used
            to look into:
                conditional_fieldsets = {
                    '1000': ...}
        """
        visit_code = None
        appointment_model_cls = django_apps.get_model(self.appointment_model)
        appointment_id = request.GET.get("appointment")
        if appointment_id and UUID_PATTERN.match(appointment_id):
            try:
                appointment = appointment_model_cls.objects.get(pk=appointment_id)
            except ObjectDoesNotExist:
                pass
            else:
                visit_code = appointment.visit_code
                if appointment.visit_code_sequence != 0:
                    visit_code = f"{visit_code}.{appointment.visit_code_sequence}"
        return visit_code

    def get_fieldsets(self, request, obj=None):
        """Returns fieldsets after modifications declared in
        "conditional" dictionaries.
        """
        fieldsets = super().get_fieldsets(request, obj=obj)
        fieldsets = Fieldsets(fieldsets=fieldsets)
        key = self.get_key(request=request)
        fieldset = self.conditional_fieldsets.get(key)
        if fieldset:
            try:
                fieldset = tuple(fieldset)
            except TypeError:
                fieldset = (fieldset,)
            for f in fieldset:
                fieldsets.add_fieldset(fieldset=f)
        fieldlist = self.conditional_fieldlists.get(key)
        if fieldlist:
            try:
                fieldsets.insert_fields(
                    *fieldlist.insert_fields,
                    insert_after=fieldlist.insert_after,
                    section=fieldlist.section,
                )
            except AttributeError:
                pass
            try:
                fieldsets.remove_fields(*fieldlist.remove_fields, section=fieldlist.section)
            except AttributeError:
                pass
        fieldsets.move_to_end(self.fieldsets_move_to_end)
        return fieldsets.fieldsets
