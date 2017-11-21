import string

from django.core.exceptions import ValidationError
from django.db.models.constants import LOOKUP_SEP
from django_crypto_fields.fields import BaseField as BaseEncryptedField


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
        * encrypt: replaces encrypted values with `encrypted_label`.
            (Default: True). If False will decrypt the value.
        * additional_values: a class to provide additional attrs
            to get if field_name is not on the model_obj and
            not a lookup.
    """

    encrypted_label = '<encrypted>'
    m2m_delimiter = ';'

    def __init__(self, field_name=None, model_obj=None,
                 lookups=None, encrypt=None, additional_values=None):
        self._value = None
        self.additional_values = additional_values
        self.field_name = field_name
        self.model_obj = model_obj
        self.lookups = lookups or {}
        self.model_cls = self.model_obj.__class__
        self.encrypt = True if encrypt is None else encrypt

    @property
    def value(self):
        if not self._value:
            try:
                self._value = self.get_field_value(
                    self.model_obj, self.field_name)
            except ValueGetterUnknownField as e:
                try:
                    self._value = getattr(self.model_obj, e.code)
                except AttributeError:
                    if self.additional_values:
                        self._value = getattr(self.additional_values, e.code)
                    else:
                        raise ValueGetterUnknownField(e)
            if self._value is None:
                self._value = ''
            self._value = self.strip_value(self._value)
        return self._value

    def get_field_value(self, model_obj=None, field_name=None):
        """Returns a field value.
        """
        value = ''
        for f in model_obj.__class__._meta.fields:
            if (f.name == field_name and issubclass(f.__class__, BaseEncryptedField)
                    and self.encrypt):
                value = self.encrypted_label
        if value != self.encrypted_label:
            try:
                value = self.getattr(model_obj, field_name)
            except AttributeError:
                if field_name in self.lookups:
                    value = self.get_lookup_value(
                        model_obj=model_obj,
                        field_name=field_name)
                elif field_name in self.m2m_field_names:
                    value = self.get_m2m_value(model_obj, field_name)
                else:
                    raise ValueGetterUnknownField(
                        f'Unknown field name. Got {field_name}.', code=field_name)
        return value

    def get_lookup_value(self, model_obj=None, field_name=None):
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
                    f'Invalid lookup string. Got {lookup_string}')
        return value

    @property
    def m2m_field_names(self):
        """Returns the list of m2m field names for this model.
        """
        return [m2m.name for m2m in self.model_cls._meta.many_to_many]

    def get_m2m_value(self, model_obj=None, field_name=None):
        """Returns an m2m field value as a delimited string.
        """
        return self.m2m_delimiter.join(
            [value.name for value in getattr(model_obj, field_name).all()])

    def strip_value(self, value):
        """Returns a string cleaned of \n\t\r and double spaces.
        """
        try:
            value = value.replace(string.whitespace, ' ')
        except (TypeError, AttributeError):
            pass
        else:
            value = ' '.join(value.split())
        return value
