from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured, FieldError

from .cap import ALL_SITES
from .exceptions import SubjectTypeCapError


class SubjectTypeCapMixin:

    def get_cap(self, subject_type_name=None, model=None, study_site=None):
        """Returns a Cap instance for a given subject_type_name and model.

        If \'model\' is not provided, assume this is a model and try for Meta.label_lower
        If "\'subject_type_name\', assume this is a model and try for Meta.subject_type_name or self.subject_type."""
        app_config = django_apps.get_app_config('edc_protocol')
        if not subject_type_name:
            subject_type_name = self.get_subject_type_name()
        if not model:
            try:
                model = self._meta.label_lower
            except AttributeError as e:
                raise SubjectTypeCapError(
                    'To get a subject type Cap, \'model\' is required if mixin is not declared with a model. '
                    'Got {}'.format(str(e)))
        if not study_site:
            try:
                study_site = self.study_site
                if not study_site:
                    raise SubjectTypeCapError('Study site cannot be None.')
            except AttributeError:
                study_site = ALL_SITES
        cap = app_config.subject_types.get('{}:{}:{}'.format(
            subject_type_name, model, study_site))
        if not cap:
            cap = app_config.subject_types.get('{}:{}:{}'.format(
                subject_type_name, model, ALL_SITES))
            if not cap:
                raise SubjectTypeCapError(
                    'Unknown cap. Got {}:{}:{}. Expected one of {}. See edc_protocol'.format(
                        subject_type_name, model, study_site, app_config.subject_types.keys()))
        return cap

    def fetch_or_raise_on_cap_met(self, subject_type_name=None, model=None, count=None):
        """Raises an exception if cap reached for this model and subject_type."""
        cap = self.get_cap(subject_type_name, model)
        if count is None:
            try:
                count = self.__class__.objects.filter(subject_type=cap.subject_type_name).count()
            except FieldError:
                count = self.__class__.objects.all().count()
        if count >= cap.max_subjects:
            raise SubjectTypeCapError('Subject type Cap reached for \'{}\'.'.format(cap))
        return count, cap.max_subjects

    def get_subject_type_name(self):
        """Returns the subject_type_name as a string.

        Tries _meta.subject_type_name and if None tries self.subject_type.

        Verifies subject_type_name is valid."""
        subject_type_name = None
        app_config = django_apps.get_app_config('edc_protocol')
        try:
            subject_type_name = self._meta.subject_type
        except AttributeError:
            pass
        if not subject_type_name:
            try:
                subject_type_name = self.subject_type
            except AttributeError:
                ImproperlyConfigured(
                    'Unable to determine \'subject_type\' for model using SubjectTypeCapMixin. Try specifying '
                    ' Meta attr \'subject_type_name\' or defining a subject_type property on the model.')
        subject_type_names = []
        for label in app_config.subject_types:
            subject_type_names.append(label.split(':')[0])
        if subject_type_name not in subject_type_names:
            raise SubjectTypeCapError(
                'Invalid subject type. Got \'{}\'. see \'edc_protocol.app_config\''.format(subject_type_name))
        return subject_type_name
