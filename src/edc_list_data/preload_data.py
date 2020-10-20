import sys

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.management.color import color_style
from django.db.models.deletion import ProtectedError
from django.db.utils import IntegrityError

from .load_list_data import load_list_data

style = color_style()


class PreloadData:
    def __init__(
        self,
        list_data=None,
        model_data=None,
        unique_field_data=None,
        list_data_model_name=None,
        apps=None,
    ):
        self.list_data = list_data or {}
        self.model_data = model_data or {}
        self.unique_field_data = unique_field_data or {}

        if self.list_data:
            self.load_list_data(model_name=list_data_model_name, apps=apps)

        if self.model_data:
            self.load_model_data()

        if self.unique_field_data:
            self.update_unique_field_data()

    def load_list_data(self, model_name=None, apps=None):
        load_list_data(self.list_data, model_name=model_name, apps=apps)

    def load_model_data(self, apps=None):
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
        for model_name, options in self.model_data.items():
            try:
                model_name, unique_field = model_name
            except ValueError:
                unique_field = None
            model = apps.get_model(model_name)
            unique_field = unique_field or self.guess_unique_field(model)
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

    def update_unique_field_data(self, apps=None):
        """Updates the values of the unique fields in a model.

        Model must have a unique field and the record must exist

        Format:
            {model_name1: {unique_field_name: (current_value, new_value)},
             model_name2: {unique_field_name: (current_value, new_value)},
             ...}
        """
        apps = apps or django_apps
        for model_name, data in self.unique_field_data.items():
            model = apps.get_model(*model_name.split("."))
            for field, values in data.items():
                try:
                    model.objects.get(**{field: values[1]})
                except ObjectDoesNotExist:
                    try:
                        obj = model.objects.get(**{field: values[0]})
                    except model.DoesNotExist as e:
                        sys.stdout.write(style.ERROR(str(e) + "\n"))
                    except MultipleObjectsReturned as e:
                        sys.stdout.write(style.ERROR(str(e) + "\n"))
                    else:
                        setattr(obj, field, values[1])
                        obj.save()
                else:
                    try:
                        obj = model.objects.get(**{field: values[0]})
                    except model.DoesNotExist:
                        pass
                    else:
                        try:
                            obj.delete()
                        except ProtectedError:
                            pass

    @staticmethod
    def guess_unique_field(model):
        """Returns the first field name for a unique field.
        """
        unique_field = None
        for field in model._meta.get_fields():
            try:
                if field.unique and field.name != "id":
                    unique_field = field.name
                    break
            except AttributeError:
                pass
        return unique_field
