from django.apps import apps as django_apps
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from edc_model import models as edc_models


class ExportPermissionsFixer:
    def __init__(self, app_label=None, verbose=None):
        if app_label:
            self.app_configs = [django_apps.get_app_config(app_label)]
        else:
            self.app_configs = django_apps.get_app_configs()
        self.verbose = verbose if verbose is not None else False

    def fix(self):
        """Add "import" and "export" to default permissions of add, change, delete, view.

        Needed for BaseUuidModel models with an initial migration created before edc==0.1.24.

        Provided for ``django-import-export`` integration
        """

        if self.verbose:
            print("Adding `import` and `export` to default permissions.")
        for app_config in self.app_configs:
            if self.verbose:
                print(f"  * updating {app_config.name}")
            for model in app_config.get_models():
                self.fix_for_model(model)
        if self.verbose:
            print("Done")

    def fix_for_model(self, model):
        if issubclass(model, (edc_models.BaseUuidModel,)):
            if self.verbose:
                print(f"    - {model._meta.label_lower}")
            try:
                content_type = ContentType.objects.get(
                    app_label=model._meta.app_label, model=model._meta.object_name,
                )
            except ObjectDoesNotExist as e:
                raise ObjectDoesNotExist(f"{e} Got {model}.")
            for action in ["import", "export"]:
                codename = f"{action}_{model._meta.label_lower.split('.')[1]}"
                opts = dict(content_type=content_type, codename=codename)
                try:
                    obj = Permission.objects.get(**opts)
                except ObjectDoesNotExist:
                    opts.update(name=f"Can {action} {model._meta.verbose_name}")
                    Permission.objects.create(**opts)
                    if self.verbose:
                        print(f"       created for {model._meta.label_lower}")
                else:
                    obj.name = f"Can {action} {model._meta.verbose_name}"
                    obj.save()
