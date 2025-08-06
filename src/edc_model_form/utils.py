from typing import Any

from django import forms


def get_field_or_raise(name: str, msg: str, cleaned_data: dict, instance) -> Any:
    """Returns a field value from cleaned_data if the key
    exists, or from the model instance.

    Raises if field value is none.
    """
    if name in cleaned_data and not cleaned_data.get(name):
        raise forms.ValidationError({"__all__": msg})
    value = cleaned_data.get(name, getattr(instance, name))
    if not value:
        raise forms.ValidationError({"__all__": msg})
    return value
