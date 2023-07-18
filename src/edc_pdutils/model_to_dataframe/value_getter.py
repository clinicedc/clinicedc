from __future__ import annotations

import string
from typing import TYPE_CHECKING, Any, Type

from django.core.exceptions import ValidationError
from django.db.models import Manager
from django.db.models.constants import LOOKUP_SEP
from django_crypto_fields.fields import BaseField as BaseEncryptedField

if TYPE_CHECKING:
    from edc_model.models import BaseUuidModel

    class MyModel(BaseUuidModel):
        class Meta(BaseUuidModel.Meta):
            pass


class ValueGetterUnknownField(ValidationError):
    pass


class ValueGetterInvalidLookup(ValidationError):
    pass


class ValueGetter:

    """A class to retrieve a field value from a django models
    instance.

    Keyword Args:
        * field_name: model instance field name
        * model_obj: model instance
        * lookups: a dictionary of {field_name: lookup, ...} where
            lookup is a django-style lookup string
            e.g. 'subject_visit__appointment__visit_code'.
        * decrypt: If False, replaces encrypted values with `encrypted_label`.
            (Default: False). If True will show the value.
        * additional_values: a class to provide additional attrs
            to get if field_name is not on the model_obj and
            not a lookup.
    """

    encrypted_label: str = "<encrypted>"
    m2m_delimiter: str = ";"

    def __init__(
        self,
        field_name: str = None,
        model_obj=None,
        lookups: dict | None = None,
        encrypt: bool | None = None,
        additional_values=None,
    ):
        self._value: Any = None
        self.additional_values = additional_values
        self.encrypt = encrypt
        self.field_name = field_name
        self.lookups = lookups or {}
        self.model_obj = model_obj
        self.model_cls = self.model_obj.__class__

    @property
    def value(self) -> Any:
        """Returns the "value"."""
        if not self._value:
            try:
                self._value = self._get_field_value(self.model_obj, self.field_name)
            except ValueGetterUnknownField as e:
                try:
                    self._value = getattr(self.model_obj, e.code)
                except AttributeError:
                    if self.additional_values:
                        self._value = getattr(self.additional_values, e.code)
                    else:
                        raise ValueGetterUnknownField(e)
            if self._value is None:
                self._value = ""
            self._value = self.strip_value(self._value)
        return self._value

    def _get_field_value(self, model_obj: Type[MyModel] = None, field_name: str = None) -> Any:
        """Returns a field value.

        1. Tries to access a field as a model instance attribute;
        2. Via a lookup (e.g. get subject_identifier via subject_visit__subject_identifier)
        3. as an m2m
        """
        value = ""
        for f in model_obj.__class__._meta.get_fields():
            if (
                f.name == field_name
                and issubclass(f.__class__, BaseEncryptedField)
                and self.encrypt
            ):
                value = self.encrypted_label
        if value != self.encrypted_label:
            try:
                value = getattr(model_obj, field_name)
            except AttributeError:
                if field_name in self.lookups:
                    value = self.get_lookup_value(model_obj=model_obj, field_name=field_name)
                else:
                    raise ValueGetterUnknownField(
                        f"Unknown field name. Perhaps add a lookup. " f"Got {field_name}.",
                        code=field_name,
                    )
            if isinstance(value, Manager):
                if field_name in self.m2m_field_names:
                    value = self.get_m2m_value(model_obj, field_name)
                else:
                    raise ValueGetterUnknownField(
                        f"Unknown field name. Got {field_name}.", code=field_name
                    )
        return value

    def get_lookup_value(self, model_obj: Type[MyModel] = None, field_name: str = None) -> Any:
        """Returns the field value by following the lookup string
        to a related instance.
        """
        value = model_obj
        lookup_string = self.lookups.get(field_name)
        for attr in lookup_string.split(LOOKUP_SEP):
            try:
                value = getattr(value, attr)
            except AttributeError:
                raise ValueGetterInvalidLookup(
                    f"Invalid lookup string or value not set. Got {lookup_string}"
                )
        return value

    @property
    def m2m_field_names(self) -> list[str]:
        """Returns the list of m2m field names for this model."""
        return [m2m.name for m2m in self.model_cls._meta.many_to_many]

    def get_m2m_value(self, model_obj: Type[MyModel] = None, field_name: str = None) -> str:
        """Returns an m2m field value as a delimited string."""
        return self.m2m_delimiter.join(
            [value.name for value in getattr(model_obj, field_name).all()]
        )

    def strip_value(self, value: Any) -> Any:
        """Returns a string cleaned of \n\t\r and double spaces."""
        try:
            value = value.replace(string.whitespace, " ")
        except (TypeError, AttributeError):
            pass
        else:
            value = " ".join(value.split())
        return value
