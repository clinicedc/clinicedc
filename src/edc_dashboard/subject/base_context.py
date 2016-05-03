import copy

from django.apps import apps
from django.core.urlresolvers import reverse, NoReverseMatch

from edc_base.utils import convert_from_camel
from edc_constants.constants import (
    NOT_REQUIRED, ADDITIONAL, IN_PROGRESS, NEW, KEYED, UNKEYED, NEW_APPT, COMPLETE_APPT)


class BaseContext(object):

    """A Class used by the dashboard when rendering the list of
    scheduled entries to display under "Scheduled Forms".

    .. note:: "model" is the data form or requisition to be keyed
    and "crf entry" is the meta data instance."""

    meta_data_model = None

    def __init__(self, meta_data_instance, appointment, visit_model):
        self._instance = None
        self.appointment = appointment
        self.visit_model = visit_model
        self.meta_data_instance = meta_data_instance

    @property
    def context(self):
        """Returns a dictionary for the template context including all
        fields from ScheduledEntryMetaData, URLs, etc.

        .. note:: The main purpose of this class is to return the template context."""
        context = copy.deepcopy(self.meta_data_instance.__dict__)
        for key in [key for key in context.keys() if key.startswith('_')]:
            del context[key]
        context.update(
            IN_PROGRESS=IN_PROGRESS,
            NEW=NEW,
            KEYED=KEYED,
            UNKEYED=UNKEYED,
            NOT_REQUIRED=NOT_REQUIRED,
            NEW_APPT=NEW_APPT,
            COMPLETE_APPT=COMPLETE_APPT,
        )
        context.update({
            'user_created': None,
            'user_modified': None,
            'created': None,
            'modified': None,
            'status': self.meta_data_instance.entry_status,
            'label': self.model._meta.verbose_name,
            'model_url': self.model_url,
            'meta_data_model_change_url': self.meta_data_model_change_url,
            'databrowse_url': self.databrowse_url,
            'audit_trail_url': self.audit_trail_url})
        if self.instance:
            context.update({
                'model_pk': self.instance.pk,
                'user_created': self.instance.user_created,
                'user_modified': self.instance.user_modified,
                'created': self.instance.created,
                'modified': self.instance.modified})
        context = self.contribute_to_context(context)
        return context

    def contribute_to_context(self, context):
        """Returns the context after adding or updating values.

        Users may override."""
        return context

    @property
    def instance(self):
        """Sets to the model instance referred to by the crf entry."""
        if not self._instance:
            options = {convert_from_camel(self.visit_instance._meta.object_name): self.visit_instance}
            if self.model.objects.filter(**options):
                self._instance = self.model.objects.get(**options)
        return self._instance

    @property
    def visit_instance(self):
        """Returns and instance of the visit model filtered on appointment."""
        return self.visit_model.objects.get(appointment=self.appointment)

    @property
    def required(self):
        return self.meta_data_instance.crf_entry_status != NOT_REQUIRED

    @property
    def not_required(self):
        return self.meta_data_instance.crf_entry_status == NOT_REQUIRED

    @property
    def additional(self):
        return self.meta_data_instance.crf_entry.additional == ADDITIONAL

    @property
    def model(self):
        """Returns the model class of the model referred to by the crf entry."""
        app_label = self.meta_data_instance.crf_entry.app_label
        model_name = self.meta_data_instance.crf_entry.model_name
        return apps.get_model(app_label, model_name)

    @property
    def model_url(self):
        """Returns the URL to the model referred to by the scheduled
        entry meta data if the current appointment is 'in progress'."""
        model_url = None
        if self.appointment.appt_status == IN_PROGRESS:
            if self.meta_data_instance.entry_status == NOT_REQUIRED:
                model_url = None
            elif not self.instance:
                model_url = reverse(
                    'admin:{app_label}_{model_name}_add'.format(
                        app_label=self.model._meta.app_label,
                        model_name=self.model._meta.object_name.lower()))
            elif self.instance:
                model_url = reverse(
                    'admin:{app_label}_{model_name}_change'.format(
                        app_label=self.model._meta.app_label,
                        model_name=self.model._meta.object_name.lower()), args=(self.instance.pk, ))
        return model_url

    @property
    def meta_data_model_change_url(self):
        """Returns the admin change URL for the scheduled entry meta data
        instance if the current appointment is 'in progress'."""
        if self.appointment.appt_status == IN_PROGRESS:
            return reverse('admin:{app_label}_{model_name}_change'.format(
                app_label=self.meta_data_model._meta.app_label,
                model_name=self.meta_data_model._meta.object_name.lower()), args=(self.meta_data_instance.pk, ))
        return ''

    @property
    def databrowse_url(self):
        """Returns the URL to display this model instance using databrowse."""
        url = ''
        if self.instance:
            try:
                url = '/databrowse/{app_label}/{model_name}/objects/{pk}/'.format(
                    app_label=self.model._meta.app_label,
                    model_name=self.model._meta.object_name.lower(),
                    pk=self.instance.pk)
            except NoReverseMatch:
                pass
        return url

    @property
    def audit_trail_url(self):
        """returns the URL to display the audit trail for this model instance."""
        if self.instance:
            return '/audit_trail/{app_label}/{model_name}/{subject_identifier}/'.format(
                app_label=self.model._meta.app_label,
                model_name=self.model._meta.object_name.lower(),
                subject_identifier=self.instance.get_subject_identifier())
        return ''
