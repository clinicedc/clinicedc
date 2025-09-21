from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import CharField, TextField

from edc_constants.constants import NULL_STRING
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
    def registration_model(self) -> type[RegisteredSubject]:
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
        with contextlib.suppress(AttributeError):
            value = str(value.hex)
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
        for fname, value in self.__dict__.items():
            if fname not in (*DEFAULT_BASE_FIELDS, "_state"):
                try:
                    getattr(rs, fname)
                except AttributeError:
                    pass
                else:
                    value = (  # noqa: PLW2901
                        NULL_STRING
                        if value is None
                        and isinstance(rs._meta.get_field(fname), (CharField, TextField))
                        else value
                    )
                    registration_options.update({fname: value})
        registration_identifier = registration_options.get("registration_identifier")
        if registration_identifier:
            registration_options["registration_identifier"] = self.to_string(
                registration_identifier
            )
        return registration_options

    class Meta:
        abstract = True
