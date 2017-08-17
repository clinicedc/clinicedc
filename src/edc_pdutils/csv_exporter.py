import os
import sys

from django.apps import apps as django_apps
from django.core.management.color import color_style
from edc_base.utils import get_utcnow

from .model_to_dataframe import ModelToDataframe

app_config = django_apps.get_app_config('edc_pdutils')

style = color_style()


class CsvExporter:

    delimiter = '|'
    encoding = 'utf-8'
    excluded_model_names = ['incomingtransaction',
                            'outgoingtransaction',
                            'crypt']
    export_folder = app_config.export_folder
    dataframe_maker_cls = ModelToDataframe

    def __init__(self, recipe=None, model=None, queryset=None,
                 include_index=None, **kwargs):
        self.include_index = include_index
        self.queryset = queryset
        if recipe:
            self.export_folder = recipe.out_path
            model = recipe.model
        self.dataframe_maker = self.dataframe_maker_cls(
            model=model, queryset=self.queryset, **kwargs)
        self.model = self.dataframe_maker.model
        self.encrypted_models, self.unencrypted_models = self.categorize_models()

    def to_csv(self, exists_ok=None):
        encrypted = True if self.model_cls in self.encrypted_models else False
        msg = f'{self.model} {"(encrypted)" if encrypted else ""}'
        sys.stdout.write(msg + '\r')
        count = self.model_cls.objects.all().count()
        path = None
        if count > 0:
            path = os.path.join(self.export_folder, self.get_filename())
            if os.path.exists(path) and not exists_ok:
                sys.stdout.write(style.ERROR(
                    f'File \'{path}\' exists! Got model={self.model}.\n'))
            else:
                sys.stdout.write(f'( ) {msg} ...     \r')
                self.dataframe_maker.dataframe.to_csv(
                    columns=self.dataframe_maker.dataframe.columns,
                    path_or_buf=path,
                    index=self.include_index,
                    encoding=self.encoding,
                    sep=self.delimiter)
                sys.stdout.write(f'(*) {msg}           \n')
        else:
            sys.stdout.write(f'(?) {msg} empty  \n')
        return path

    def categorize_models(self):
        """Returns a tuple of two lists (encrypted_models, unencrypted_models).
        """
        unencrypted_models = []
        encrypted_models = []
        for app_config in django_apps.get_app_configs():
            for model in app_config.get_models():
                for field in model._meta.fields:
                    if hasattr(field, 'field_cryptor'):
                        encrypted_models.append(model)
                        model = None
                        break
                if model:
                    unencrypted_models.append(model)
        unencrypted_models = [
            m for m in unencrypted_models
            if m._meta.model_name not in self.excluded_model_names]
        unencrypted_models.sort(
            key=lambda x: x._meta.label_lower)
        encrypted_models = [
            m for m in encrypted_models
            if m._meta.model_name not in self.excluded_model_names]
        encrypted_models.sort(
            key=lambda x: x._meta.label_lower)
        return encrypted_models, unencrypted_models

    @property
    def model_cls(self):
        return django_apps.get_model(self.model)

    def get_filename(self):
        """Returns a CSV filename using the model label lower
        and the current date.
        """
        dt = get_utcnow()
        formatted_model = self.model_cls._meta.label_lower.replace(".", "_")
        formatted_date = dt.strftime('%Y%m%d%H%M%S')
        return f'{formatted_model}_{formatted_date}.csv'
