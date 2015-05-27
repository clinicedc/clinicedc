import itertools
import six

from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_model

from edc.base.model.models import BaseModel


class MembershipFormHelper(object):

    def __init__(self, *args, **kwargs):
        self._keyed = None
        self._unkeyed = None
        self._grouping_key = None
        self._category = None
        self._model = None

    def get_membership_models_for(self, registered_subject, membership_form_category, **kwargs):

        """ Returns dict of keyed model instances and unkeyed model classes or "membership forms" for a given registered_subject.

        Specify the registered_subject and the membership_form_category.
        """
        ScheduleGroup = get_model('edc_visit_schedule', 'ScheduleGroup')
        extra_grouping_key = kwargs.get("exclude_others_if_keyed_model_name", None)
        self._set_keyed()
        self._set_unkeyed()
        self._set_category(membership_form_category)
        for schedule_group in ScheduleGroup.objects.filter(membership_form__category__iexact=self._get_category()):
            self._set_model(schedule_group=schedule_group)
            if self._get_model().objects.filter(registered_subject_id=registered_subject.pk):
                self._add_keyed(schedule_group.grouping_key, self._get_model().objects.get(registered_subject=registered_subject))
            else:
                self._add_unkeyed(schedule_group.grouping_key, self._get_model())
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
        from edc.subject.appointment_helper.models import BaseAppointmentMixin
        if not group:
            group = 'no_group'
        if not isinstance(group, six.string_types):
            raise TypeError('Expected parameter group to be a string')
        if not isinstance(obj, BaseAppointmentMixin):
            raise TypeError('Expected an instance of a model class using mixin BaseAppointmentMixin. Models {0} of group \'{1}\' is being used as membership form so must be a subclass of this mixin.'.format(obj.__class__, group))
        if group in self._get_keyed():
            self._get_keyed()[group].append(obj)
        else:
            self._get_keyed().update({group: [obj]})

    def _set_unkeyed(self):
        self._unkeyed = {}

    def _add_unkeyed(self, group, cls):
        from edc.subject.appointment_helper.models import BaseAppointmentMixin
        if not group:
            group = 'no_group'
        if not isinstance(group, six.string_types):
            raise TypeError('Expected parameter group to be a string')
        if not issubclass(cls, BaseAppointmentMixin):
            raise TypeError('Expected a model class using mixin BaseAppointmentMixin')
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

    def _set_model(self, cls=None, schedule_group=None):
        """Sets the model class of the model that is either keyed or unkeyed.

        Either uses the content_type associated with the MembershipForm instance
        or uses the cls parameter.

        Model class must have a key to registered_subject and may not be None."""
        self._model = None
        ScheduleGroup = get_model('edc_visit_schedule', 'ScheduleGroup')
        if isinstance(schedule_group, ScheduleGroup):
            if not schedule_group.membership_form.content_type_map.model_class():
                raise ImproperlyConfigured('Cannot get model class from content_type_map for schedule group \'{0}\' using \'{1}\'. Update content_type_map?'.format(schedule_group, schedule_group.membership_form))
            else:
                self._model = schedule_group.membership_form.content_type_map.model_class()
        if isinstance(cls, BaseModel):
            self._model = cls
        if 'registered_subject' not in dir(self._model):
            raise ImproperlyConfigured('Model require attribute \'registered_subject\'. Model \'%s\' does not have this attribute but is listed as a membership form.' % schedule_group.membership_form.content_type_map.name)
        if not self._model:
            raise TypeError('Attribute _model may not be None.')

    def _get_model(self):
        if not self._model:
            self._set_model()
        return self._model

    def _is_configured_for_category(self, category=None):
        """Confirms membership forms exist for this category.

        .. note:: category may be a string delimited by commas like 'subject, maternal' or just 'subject'. Below
                  the string values are converted to listed and concatenated into one unique list."""
        MembershipForm = get_model('edc_visit_schedule', 'MembershipForm')
        ScheduleGroup = get_model('edc_visit_schedule', 'ScheduleGroup')
        # convert MembershipForm category field values into a unique list
        categories = list(set([y.strip() for y in list(itertools.chain(*[m['category'].split(',') for m in MembershipForm.objects.values('category').order_by('category').distinct()]))]))
        if category not in categories:
            raise ImproperlyConfigured('Can\'t find any membership forms! Have you configured any for category \'{0}\'. Must be one of {1}.'.format(category, [m['category'] for m in MembershipForm.objects.values('category').order_by('category').distinct()]))
        # convert ScheduleGroup category field values into a unique list
        categories = list(set([y.strip() for y in list(itertools.chain(*[m['membership_form__category'].split(',') for m in ScheduleGroup.objects.values('membership_form__category').order_by('membership_form__category').distinct()]))]))
        if category not in categories:
            raise ImproperlyConfigured('Can\'t find any schedule groups! Have you configured any for category \'{0}\'.'.format(category))
        return True

    def _remove_unkeyed_by_grouping_key(self):
        """Removes from unkeyed if any member of group is in keyed."""
        for grouping_key in self._get_keyed():
            if grouping_key in self._get_unkeyed():
                del self._get_unkeyed()[grouping_key]

    def _remove_unkeyed_by_extra_grouping_key(self, extra_grouping_key):
        """Removes from unkeyed if the unkeyed object name startswith string extra_grouping_key."""
        if extra_grouping_key:
            for inst in self._get_keyed().values():
                if inst._meta.object_name.lower() == extra_grouping_key:
                    for grouping_key, cls in self._get_unkeyed().items():
                        if cls._meta.object_name.lower().startswith(extra_grouping_key):
                            del self._get_unkeyed()[grouping_key]

    def _format_for_return(self):
        keyed = []
        for inst in [inst for inst in self._get_keyed().values()]:
            if isinstance(inst, list):
                for i in inst:
                    keyed.append(i)
            else:
                keyed.append(inst)
        unkeyed = []
        for cls in [cls for cls in self._get_unkeyed().values()]:
            if isinstance(cls, list):
                for c in cls:
                    unkeyed.append(c)
            else:
                unkeyed.append(cls)
        return {'keyed': keyed, 'unkeyed': unkeyed}
