import os
import sys

from django.apps import apps as django_apps
from django.db.utils import OperationalError

from .model_to_dataframe import ModelToDataFrame


class ExportDataToCsv:

    def __init__(self, recipe=None, export_model=None, overwrite_csv=None, export_csv=None, **kwargs):
        export_csv = True if export_csv is None else export_csv
        if recipe:
            self.path = recipe.out_path
            export_model = recipe.model
        else:
            self.path = None
        self.unencrypted_models = []
        self.encrypted_models = []
        excluded_models = [
            'incomingtransaction', 'outgoingtransaction', 'crypt']
        for app_config in django_apps.get_app_configs():
            for model in app_config.get_models():
                for field in model._meta.fields:
                    if hasattr(field, 'field_cryptor'):
                        self.encrypted_models.append(model)
                        model = None
                        break
                if model:
                    self.unencrypted_models.append(model)
        self.unencrypted_models = [
            m for m in self.unencrypted_models
            if m._meta.model_name not in excluded_models]
        self.unencrypted_models.sort(
            key=lambda x: x._meta.label_lower)
        self.encrypted_models = [
            m for m in self.encrypted_models
            if m._meta.model_name not in excluded_models]
        self.encrypted_models.sort(
            key=lambda x: x._meta.label_lower)
        if export_csv:
            self.export_model_to_csv(
                model=export_model, overwrite_csv=overwrite_csv)

    def export_model_to_csv(self, model, overwrite_csv=None):
        overwrite_csv = False if overwrite_csv is None else False
        encrypted = True if model in self.encrypted_models else False
        msg = '{}{}'.format(
            model._meta.label_lower, ' (encrypted)' if encrypted else '')
        sys.stdout.write(msg + '\r')
        count = model.objects.all().count()
        if count > 0:
            path_or_buf = os.path.join(
                self.path_root, model._meta.app_label,
                '{}.csv'.format(model._meta.model_name))
            if os.path.exists(path_or_buf):
                sys.stdout.write(
                    '{} exists ({} records).\n'.format(msg, count))
            if ((not os.path.exists(path_or_buf))
                    or (os.path.exists(path_or_buf) and overwrite_csv)):
                sys.stdout.write('{} creating **** \r'.format(msg))
                try:
                    m2df = ModelToDataFrame(model)
                except OperationalError as err:
                    sys.stdout.write('\nError. {}. Got {}\n\n'.format(
                        model._meta.model_name, str(err)))
                else:
                    path_or_buf = os.path.join(
                        self.path_root, model._meta.app_label,
                        '{}.csv'.format(model._meta.model_name))
                    m2df.dataframe.to_csv(
                        columns=m2df.columns(model.objects.all(), None),
                        path_or_buf=path_or_buf,
                        index=False,
                        encoding='utf-8',
                        sep='|')
                    sys.stdout.write('{} creating **** Done\n'.format(msg))
        else:
            sys.stdout.write('{} empty\n'.format(msg))
