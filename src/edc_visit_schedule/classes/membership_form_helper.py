from django.db import models
from django.core.exceptions import ImproperlyConfigured

from edc_base.model.models import BaseModel


class MembershipFormHelper(object):

    def __init__(self, *args, **kwargs):
        self._keyed = None
        self._unkeyed = None
        self._grouping_key = None
        self._category = None
        self._model = None

    def get_membership_models_for(self, registered_subject, membership_form_category, **kwargs):

        """ Returns dict of keyed model instances and unkeyed model
        classes or "membership forms" for a given registered_subject.

        Specify the registered_subject and the membership_form_category.
        """
        Schedule = models.get_model('edc_visit_schedule', 'Schedule')
        extra_grouping_key = kwargs.get("exclude_others_if_keyed_model_name", None)
        self._set_keyed()
        self._set_unkeyed()
        self._set_category(membership_form_category)
        for schedule in Schedule.objects.filter(membership_form__category__iexact=self._get_category()):
            self._set_model(schedule=schedule)
            if self._get_model().objects.filter(registered_subject_id=registered_subject.pk).exists():
                for obj in self._get_model().objects.filter(registered_subject_id=registered_subject.pk):
                    self._add_keyed(schedule.grouping_key, obj)
            else:
                self._add_unkeyed(schedule.grouping_key, self._get_model())
        self._remove_unkeyed_by_grouping_key()
        self._remove_unkeyed_by_extra_grouping_key(extra_grouping_key)
        return self._format_for_return()

    def _set_keyed(self):
        self._keyed = {}

    def _get_keyed(self):
        if self._keyed is None:
            self._set_keyed()
        return self._keyed

    def _add_keyed(self, group, obj):
        from edc_appointment.models import AppointmentMixin
        if not group:
            group = 'no_group'
        if not isinstance(group, basestring):
            raise TypeError('Expected parameter group to be a string')
        if not isinstance(obj, AppointmentMixin):
            raise TypeError('Expected an instance of AppointmentMixin. Models {0} of group \'{1}\' is being '
                            'used as membership form so must be a subclass of this mixin.'.format(
                                obj.__class__, group))
        if group in self._get_keyed():
            self._get_keyed()[group].append(obj)
        else:
            self._get_keyed().update({group: [obj]})

    def _set_unkeyed(self):
        self._unkeyed = {}

    def _add_unkeyed(self, group, cls):
        from edc_appointment.models import AppointmentMixin
        if not group:
            group = 'no_group'
        if not isinstance(group, basestring):
            raise TypeError('Expected parameter group to be a string')
        if not issubclass(cls, AppointmentMixin):
            raise TypeError('Expected a model class using mixin AppointmentMixin')
        if group in self._get_unkeyed():
            self._get_unkeyed()[group].append(cls)
        else:
            self._get_unkeyed().update({group: [cls]})

    def _get_unkeyed(self):
        if self._unkeyed is None:
            self._set_unkeyed()
        return self._unkeyed

    def _set_category(self, value=None):
        """Sets the category (MembershipForm.category)."""
        self._category = None
        if self._is_configured_for_category(value):
            self._category = value
        if not self._category:
            raise TypeError('Attribute category may not be None.')

    def _get_category(self):
        if not self._category:
            self._set_category()
        return self._category

    def _set_model(self, cls=None, schedule=None):
        """Sets the model class of the model that is either keyed or unkeyed.

        Either uses the content_type associated with the MembershipForm instance
        or uses the cls parameter.

        Model class must have a key to registered_subject and may not be None."""
        self._model = None
        Schedule = models.get_model('edc_visit_schedule', 'Schedule')
        if isinstance(schedule, Schedule):
            if not schedule.membership_form.content_type_map.model_class():
                raise ImproperlyConfigured(
                    'Cannot get model class from content_type_map for schedule group \'{0}\' '
                    'using \'{1}\'. Update content_type_map?'.format(
                        schedule, schedule.membership_form))
            else:
                self._model = schedule.membership_form.content_type_map.model_class()
        if isinstance(cls, BaseModel):
            self._model = cls
        if 'registered_subject' not in dir(self._model):
            raise ImproperlyConfigured(
                'Model require attribute \'registered_subject\'. Model \'%s\' does not have '
                'this attribute but is listed as a membership form.'.format(
                    schedule.membership_form.content_type_map.name))
        if not self._model:
            raise TypeError('Attribute _model may not be None.')

    def _get_model(self):
        if not self._model:
            self._set_model()
        return self._model

    def _is_configured_for_category(self, category=None):
        """Confirms membership forms exist for this category.

        .. note:: category may be a string delimited by commas like
            'subject, maternal' or just 'subject'. Below
            the string values are converted to listed and concatenated into one unique list."""
        MembershipForm = models.get_model('edc_visit_schedule', 'MembershipForm')
        Schedule = models.get_model('edc_visit_schedule', 'Schedule')
        # convert MembershipForm category field values into a unique list
        categories = []
        for membership_form in MembershipForm.objects.all():
            for item in membership_form.category.split(','):
                categories.append(item.strip())
        categories = list(set(categories))
        if category not in categories:
            raise ImproperlyConfigured(
                'Can\'t find any membership forms! Have you configured any for category'
                ' \'{0}\'. Must be one of {1}.'.format(
                    category, categories))
        # convert Schedule category field values into a unique list
        for scheduled_group in Schedule.objects.all():
            for item in scheduled_group.membership_form.category.split(','):
                categories.append(item.strip())
        categories = list(set(categories))
        if category not in categories:
            raise ImproperlyConfigured(
                'Can\'t find any schedule groups! Have you configured any for category \'{0}\'.'.format(category))
        return True

    def _remove_unkeyed_by_grouping_key(self):
        """Removes from unkeyed if any member of group is in keyed."""
        for grouping_key in self._get_keyed():
            if grouping_key in self._get_unkeyed():
                del self._get_unkeyed()[grouping_key]

    def _remove_unkeyed_by_extra_grouping_key(self, extra_grouping_key):
        """Removes from unkeyed if the unkeyed object name startswith string extra_grouping_key."""
        if extra_grouping_key:
            for inst in self._get_keyed().itervalues():
                if inst._meta.object_name.lower() == extra_grouping_key:
                    for grouping_key, cls in self._get_unkeyed().iteritems():
                        if cls._meta.object_name.lower().startswith(extra_grouping_key):
                            del self._get_unkeyed()[grouping_key]

    def _format_for_return(self):
        keyed = []
        for inst in [inst for inst in self._get_keyed().itervalues()]:
            if isinstance(inst, list):
                for i in inst:
                    keyed.append(i)
            else:
                keyed.append(inst)
        unkeyed = []
        for cls in [cls for cls in self._get_unkeyed().itervalues()]:
            if isinstance(cls, list):
                for c in cls:
                    unkeyed.append(c)
            else:
                unkeyed.append(cls)
        return {'keyed': keyed, 'unkeyed': unkeyed}
