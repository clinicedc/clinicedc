from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured
from django.db import models

from edc_base.model_mixins import DEFAULT_BASE_FIELDS


class UpdatesOrCreatesRegistrationModelMixin(models.Model):

    """A model mixin that creates or updates RegisteredSubject
    on post_save signal.
    """

    @property
    def registration_model(self):
        """Returns the RegisteredSubject model, Do not override.
        """
        return django_apps.get_app_config('edc_registration').model

    def registration_update_or_create(self):
        """Creates or Updates the registration model with attributes
        from this instance.

        Called from the signal
        """
        self.registration_raise_on_not_unique()
        if not getattr(self, self.registration_unique_field):
            raise TypeError(
                'Cannot update or create RegisteredSubject. Got {} '
                'is None.'.format(self.registration_unique_field))
        try:
            obj = self.registration_model.objects.get(
                **{'registration_identifier':
                   getattr(self, self.registration_unique_field)})
        except self.registration_model.DoesNotExist:
            pass
        else:
            self.registration_raise_on_illegal_value_change(obj)
        registered_subject, created = self.registration_model.objects.update_or_create(
            **{'registration_identifier': getattr(self, self.registration_unique_field)},
            defaults=self.registration_options)
        return registered_subject, created

    @property
    def registration_unique_field(self):
        return 'registration_identifier'

    def registration_raise_on_illegal_value_change(self, registered_subject):
        """Raises an exception if a value changes between
        updates.

        Values are available in `registration_options`.
        """
        pass

    def registration_raise_on_not_unique(self):
        """Asserts the field specified for update_or_create is unique.
        """
        unique_fields = []
        for f in self.registration_model._meta.get_fields():
            try:
                if f.unique:
                    unique_fields.append(f.name)
            except AttributeError:
                pass
        if self.registration_unique_field not in unique_fields:
            raise ImproperlyConfigured('Field is not unique. Got {}.{}'.format(
                self._meta.label_lower, self.registration_unique_field))

    @property
    def registration_options(self):
        """Gathers values for common attributes between the
        registration model and this instance.
        """
        registration_options = {}
        rs = self.registration_model()
        for k, v in self.__dict__.items():
            if k not in DEFAULT_BASE_FIELDS + ['_state']:
                try:
                    getattr(rs, k)
                    registration_options.update({k: v})
                except AttributeError:
                    pass
        return registration_options

    class Meta:
        abstract = True
