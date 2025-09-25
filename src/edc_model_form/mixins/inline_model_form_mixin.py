from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from django import forms
from django.apps import apps as django_apps
from django.conf import settings
from django.db.models import DateField, DateTimeField


class InlineModelFormMixinError(Exception):
    pass


class InlineModelFormMixin:
    def get_inline_field_values(self, field=None, inline_set=None):
        """Returns a list values from the inline.

        The value of fk fields is the id."""
        field_values = []
        total_forms = int(self.data.get(f"{inline_set}-TOTAL_FORMS"))
        for i in range(0, total_forms):
            if self.data.get(f"{inline_set}-{i}-DELETE") == "on":
                pass
            else:
                inline_field = f"{inline_set}-{i}-{field}"
                try:
                    field_values.append(self.data[inline_field].name)
                except KeyError:
                    break
                except AttributeError:
                    field_values.append(self.data[inline_field])
        return field_values

    def unique_inline_values_or_raise(self, field=None, inline_model=None, field_label=None):
        self.field_exists_or_raise(field, inline_model)
        inline_set = f"{inline_model.split('.')[1]}_set"
        items = self.get_inline_field_values(field=field, inline_set=inline_set)
        if len(items) != len(list(set(items))):
            field_label = field_label or field
            raise forms.ValidationError(
                f"{field_label}: The list of values below must be unique"
            )

    def dates_not_after_report_datetime(self, field=None, inline_model=None, field_label=None):
        self.field_cls_is_date_or_raise(field=field, inline_model=inline_model)
        inline_set = f"{inline_model.split('.')[1]}_set"
        dates_as_str = self.get_inline_field_values(field=field, inline_set=inline_set)
        for dte_as_str in dates_as_str:
            if dte_as_str:
                try:
                    dte = datetime.fromisoformat(dte_as_str)
                except ValueError as e:
                    raise forms.ValidationError(
                        f"{field_label}: Invalid date or date format. Got {dte_as_str}"
                    ) from e
                else:
                    if dte.astimezone(ZoneInfo(settings.TIME_ZONE)) > self.cleaned_data.get(
                        "report_datetime"
                    ):
                        raise forms.ValidationError(
                            f"{field_label}: Date cannot be after report date/time. "
                            f"Got `{dte_as_str}`."
                        )

    def field_exists_or_raise(self, field, inline_model):
        model_cls = django_apps.get_model(inline_model)
        if field not in [f.name for f in model_cls._meta.get_fields()]:
            raise InlineModelFormMixinError(
                f"Field does not exist on model class. See {self.__class__.__name__}. "
                f"Got {inline_model}.{field}."
            )
        return [f for f in model_cls._meta.get_fields() if f.name == field][0]

    def field_cls_is_date_or_raise(self, field: str, inline_model) -> Any:
        """Raises if field class on model is not a date.

        Works for DateField and DatetimeField"""
        field_obj = self.field_exists_or_raise(field, inline_model)
        if field_obj.__class__ not in [DateTimeField, DateField]:
            raise InlineModelFormMixinError(
                f"Field is not a date field class. See {self.__class__.__name__}. "
                f"Got {inline_model}.{field}."
            )
        return field_obj.__class__
