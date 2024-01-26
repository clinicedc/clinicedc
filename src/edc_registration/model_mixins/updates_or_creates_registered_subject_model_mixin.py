from __future__ import annotations

from typing import TYPE_CHECKING, Type

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from edc_model import DEFAULT_BASE_FIELDS

from ..utils import get_registered_subject_model_cls

if TYPE_CHECKING:
    from edc_registration.models import RegisteredSubject


class UpdatesOrCreatesRegistrationModelError(Exception):
    pass


class UpdatesOrCreatesRegistrationModelMixin(models.Model):

    """A model mixin that creates or updates Registration model
    (e.g. RegisteredSubject) on post_save signal.
    """

    @property
    def registration_model(self) -> Type[RegisteredSubject]:
        """Returns the Registration model"""
        return get_registered_subject_model_cls()

    def registration_update_or_create(self) -> tuple[RegisteredSubject, bool]:
        """Creates or Updates the registration model with attributes
        from this instance.

        Called from the signal.

        Note: `registration_unique_field` is typically
              "subject_identifier".
        """
        if not getattr(self, self.registration_unique_field):
            raise UpdatesOrCreatesRegistrationModelError(
                f"Cannot update or create Registration model. "
                f"Field value for '{self.registration_unique_field}' is None."
            )

        registration_value = getattr(self, self.registration_unique_field)
        registration_value = self.to_string(registration_value)
        try:
            obj = self.registration_model.objects.get(
                **{self.registered_model_unique_field: registration_value}
            )
        except ObjectDoesNotExist:
            pass
        else:
            self.registration_raise_on_illegal_value_change(obj)
        registration_obj, created = self.registration_model.objects.update_or_create(
            **{self.registered_model_unique_field: registration_value},
            defaults=self.registration_options,
        )
        return registration_obj, created

    @staticmethod
    def to_string(value) -> str:
        """Returns a string.

        Converts UUID to string using .hex.
        """
        try:
            value = str(value.hex)
        except AttributeError:
            pass
        return value

    @property
    def registration_unique_field(self) -> str:
        """Returns the field attr on YOUR model that will update
        `registered_model_unique_field`.

        Typically, `subject_identifier`.
        """
        return "subject_identifier"

    @property
    def registered_model_unique_field(self) -> str:
        """Returns the field attr on THIS model to be queried against
        the value of `registration_unique_field`.
        """
        return self.registration_unique_field

    def registration_raise_on_illegal_value_change(self, registration_obj):
        """Raises an exception if a value changes between updates.

        Values are available in `registration_options`.
        """
        pass

    @property
    def registration_options(self) -> dict:
        """Gathers values for common attributes between the
        registration model and this instance.
        """
        registration_options = {}
        rs = self.registration_model()
        for k, v in self.__dict__.items():
            if k not in DEFAULT_BASE_FIELDS + ["_state"]:
                try:
                    getattr(rs, k)
                    registration_options.update({k: v})
                except AttributeError:
                    pass
        registration_identifier = registration_options.get("registration_identifier")
        if registration_identifier:
            registration_options["registration_identifier"] = self.to_string(
                registration_identifier
            )
        return registration_options

    class Meta:
        abstract = True
