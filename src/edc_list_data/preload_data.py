import pdb
from typing import Optional

from django.apps import AppConfig
from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.color import color_style
from django.db import models
from django.db.utils import IntegrityError

from .load_list_data import load_list_data

style = color_style()


class PreloadDataError(Exception):
    pass


class PreloadData:
    def __init__(
        self,
        list_data: dict = None,
        model_data: dict = None,
        list_data_model_name: str = None,
        apps: AppConfig = None,
    ) -> None:
        self.list_data = list_data or {}
        self.model_data = model_data or {}
        self.item_count = 0
        if self.list_data:
            self.item_count += self.load_list_data(model_name=list_data_model_name, apps=apps)
        if self.model_data:
            self.item_count += self.load_model_data()

    def load_list_data(self, model_name: str = None, apps: Optional[AppConfig] = None) -> int:
        return load_list_data(self.list_data, model_name=model_name, apps=apps)

    def load_model_data(self, apps: Optional[AppConfig] = None) -> int:
        """Loads data into a model, creates or updates existing.

        Must have a unique field

        Format:
            {app_label.model1: [{field_name1: value,
                                 field_name2: value ...},...],
             (app_label.model2, unique_field_name):
               [{field_name1: value,
                 unique_field_name: value ...}, ...],
             ...}
        """
        apps = apps or django_apps
        n = 0
        for model_name, options in self.model_data.items():
            try:
                model_name, unique_field = model_name
            except ValueError:
                unique_field = None
            model = apps.get_model(model_name)
            unique_field = self.check_is_unique(
                model, unique_field
            ) or self.guess_unique_field(model)
            for opts in options:
                try:
                    obj = model.objects.get(**{unique_field: opts.get(unique_field)})
                except ObjectDoesNotExist:
                    try:
                        model.objects.create(**opts)
                    except IntegrityError:
                        pass
                else:
                    for key, value in opts.items():
                        setattr(obj, key, value)
                    obj.save()
            n += 1
        return n

    @staticmethod
    def guess_unique_field(model: models.Model) -> str:
        """Returns the first field name for a unique field."""
        unique_field = None
        for field in model._meta.get_fields():
            try:
                if field.unique and field.name != "id":
                    unique_field = field.name
                    break
            except AttributeError:
                pass
        if not unique_field:
            raise PreloadDataError(
                f"Unable to determine unique field when loading model data. See {model}."
            )
        return unique_field

    @staticmethod
    def check_is_unique(model: models.Model, unique_field: str) -> str:
        if unique_field:
            fld_cls = getattr(model, unique_field)
            unique = fld_cls.field.unique
            if not unique:
                raise PreloadDataError(f"Field is not unique. See {model}.{unique_field}")
        return unique_field
