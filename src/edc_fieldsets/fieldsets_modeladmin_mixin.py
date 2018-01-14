from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.utils.safestring import mark_safe

from .fieldsets import Fieldsets

try:
    appointment_model = settings.DEFAULT_APPOINTMENT_MODEL
except AttributeError:
    appointment_model = 'edc_appointment.appointment'
else:
    appointment_model = appointment_model or 'edc_appointment.appointment'


class FormLabel:

    def __init__(self, field, label=None, callback=None,
                 previous_instance=None,
                 previous_appointment=None):
        self.field = field
        self.label = label
        self.previous_instance = previous_instance
        self.previous_appointment = previous_appointment
        if callback:
            self.callback = callback
            if not previous_instance and not previous_appointment:
                self.previous_instance = True
        else:
            if self.previous_appointment:
                self.callback = self.previous_appointment_callback
            else:
                self.previous_instance = True
                self.callback = self.previous_instance_callback

    def previous_instance_callback(self, obj, appointment):
        return True if obj else False

    def previous_appointment_callback(self, obj, appointment):
        return True if appointment else False


class FieldsetsModelAdminMixin:

    """A class that helps modify fieldsets for subject models

    * Model is expected to have a relation to have subject_visit__appointment.
    * Expects appointment to be in GET
    """

    appointment_model = appointment_model
    # key: value where key is a visit_code. value is a fieldlist object
    conditional_fieldlists = {}
    # key: value where key is a visit code. value is a fieldsets object.
    conditional_fieldsets = {}

    custom_form_labels = {}

    fieldsets_move_to_end = None

    def update_form_labels(self, request, form):
        """Returns a form instance after modifying form labels
        referred to in custom_form_labels.

        * `label`: label to use. If none, uses current field.label
        * `callback`: any callback that accepts a single parameter.
            evaluates to True if label is to be modified.
        * `{previous}`: inserts the previous visit report datetime.

        For example:

            # use custom label if previous instance exists, otherwise use
            # model verbose_name.
            custom_form_labels = [
                FormLabel(
                    field='circumcised',
                    label='Since we last saw you in {previous}, were you circumcised?',
                    callback=lambda obj: True if obj.circumcised == NO else False)
            ]

            OR

            # use model verbose_name complete if previous instance exists.
            # in this case, previous instance should always exist
            custom_form_labels = [FormLabel(field='circumcised')]

        """
        for form_label in self.custom_form_labels:
            if form_label.field in form.base_fields:
                instance = self.get_previous_instance(request)
                appointment = self.get_previous_appointment(request)
                if form_label.previous_appointment and appointment:
                    condition = form_label.callback(instance, appointment)
                elif form_label.previous_instance and instance:
                    condition = form_label.callback(instance, appointment)
                else:
                    condition = None
                if condition:
                    label = self.format_form_label(
                        label=form_label.label or form.base_fields[
                            form_label.field].label,
                        instance=instance,
                        appointment=appointment)
                    form.base_fields[
                        form_label.field].label = mark_safe(label)
        return form

    def format_form_label(self, label=None, instance=None, appointment=None, **kwargs):
        if instance:
            report_datetime = getattr(
                instance, instance.visit_model_attr()).report_datetime
            label = label.format(
                previous=report_datetime.strftime('%B %Y'))
            return label

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj=obj, **kwargs)
        return self.update_form_labels(request, form)

    def get_previous_appointment(self, request):
        try:
            appointment = self.get_appointment(request)
        except ObjectDoesNotExist:
            return None
        else:
            return appointment.previous_by_timepoint

    def get_previous_instance(self, request, instance=None, **kwargs):
        """Returns a model instance that is the first occurrence of a previous
        instance relative to this object's appointment.

        Override this method if not a subject model.
        """
        obj = None
        appointment = instance or self.get_instance(request)
        if appointment:
            while appointment.previous_by_timepoint:
                options = {
                    '{}__appointment'.format(self.model.visit_model_attr()):
                    appointment.previous_by_timepoint}
                try:
                    obj = self.model.objects.get(**options)
                except ObjectDoesNotExist:
                    pass
                else:
                    break
                appointment = appointment.previous_by_timepoint
        return obj

    def get_appointment(self, request):
        """Returns the appointment instance for this request or None.
        """
        appointment_model_cls = django_apps.get_model(self.appointment_model)
        return appointment_model_cls.objects.get(
            pk=request.GET.get('appointment'))

    def get_instance(self, request):
        """Returns the instance that provides the key
        for the "conditional" dictionaries.

        For example: appointment.
        """
        return self.get_appointment(request)

    def get_key(self, request, obj=None):
        """Returns a string that is the key to `get` the
        value in the "conditional" dictionaries.

        For example:
            appointment.visit_code == '1000' will be used
            to look into:
                conditional_fieldsets = {
                    '1000': ...}
        """
        try:
            model_obj = self.get_instance(request)
        except ObjectDoesNotExist:
            visit_code = None
        else:
            visit_code = model_obj.visit_code
            if model_obj.visit_code_sequence != 0:
                visit_code = f'{visit_code}.{model_obj.visit_code_sequence}'
        return visit_code

    def get_fieldsets(self, request, obj=None):
        """Returns fieldsets after modifications declared in
        "conditional" dictionaries.
        """
        fieldsets = super().get_fieldsets(request, obj=obj)
        fieldsets = Fieldsets(fieldsets=fieldsets)
        key = self.get_key(request, obj)
        fieldset = self.conditional_fieldsets.get(key)
        if fieldset:
            try:
                fieldset = tuple(fieldset)
            except TypeError:
                fieldset = (fieldset, )
            for f in fieldset:
                fieldsets.add_fieldset(fieldset=f)
        fieldlist = self.conditional_fieldlists.get(key)
        if fieldlist:
            try:
                fieldsets.insert_fields(
                    *fieldlist.insert_fields,
                    insert_after=fieldlist.insert_after,
                    section=fieldlist.section)
            except AttributeError:
                pass
            try:
                fieldsets.remove_fields(
                    *fieldlist.remove_fields,
                    section=fieldlist.section)
            except AttributeError:
                pass
        fieldsets = self.update_fieldset_for_form(
            fieldsets, request)
        fieldsets.move_to_end(self.fieldsets_move_to_end)
        return fieldsets.fieldsets

    def update_fieldset_for_form(self, fieldsets, request, **kwargs):
        """Not ready"""
        if self.custom_form_labels:
            instance = self.get_instance(request)
            if instance:
                obj = self.get_previous_instance(request, instance=instance)
                if obj:
                    pass  # do something
            else:
                pass  # possibly remove field"
#                 fieldsets.remove_fields(
#                     'last_seen_circumcised')
        return fieldsets
