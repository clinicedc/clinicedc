from django.apps import apps as django_apps
from django.db import models

from edc_base.model_mixins import DEFAULT_BASE_FIELDS


class UpdatesOrCreatesRegistrationModelError(Exception):
    pass


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
        if not getattr(self, self.registration_unique_field):
            raise UpdatesOrCreatesRegistrationModelError(
                f'Cannot update or create RegisteredSubject. '
                f'Field value for \'{self.registration_unique_field}\' is None.')

        registration_value = getattr(self, self.registration_unique_field)
        registration_value = self.to_string(registration_value)
        try:
            obj = self.registration_model.objects.get(
                **{self.registered_subject_unique_field: registration_value})
        except self.registration_model.DoesNotExist:
            pass
        else:
            self.registration_raise_on_illegal_value_change(obj)
        registered_subject, created = self.registration_model.objects.update_or_create(
            **{self.registered_subject_unique_field: registration_value},
            defaults=self.registration_options)
        return registered_subject, created

    def to_string(self, value):
        """Returns a string.

        Converts UUID to string using .hex.
        """
        try:
            value = str(value.hex)
        except AttributeError:
            pass
        return value

    @property
    def registration_unique_field(self):
        """Returns the field attr on YOUR model that will update
        `registered_subject_unique_field`.
        """
        return 'subject_identifier'

    @property
    def registered_subject_unique_field(self):
        """Returns the field attr on THIS model, registered subject,
        to be queried against by the value of `registration_unique_field`.
        """
        return self.registration_unique_field

    def registration_raise_on_illegal_value_change(self, registered_subject):
        """Raises an exception if a value changes between
        updates.

        Values are available in `registration_options`.
        """
        pass

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
        registration_identifier = registration_options.get(
            'registration_identifier')
        if registration_identifier:
            registration_options['registration_identifier'] = self.to_string(
                registration_identifier)
        return registration_options

    class Meta:
        abstract = True
