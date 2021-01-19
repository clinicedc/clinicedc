from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from warnings import warn


class ExportPermissionsFixer:
    """
    Fix permissions when new permissions are added to the default list
    in the model Meta class.

    For example. see `edc_models.BaseUuidModel.Meta`

    Usage:
        fixer = ExportPermissionsFixer(warn_only=True)
        fixer.fix()
    """

    def __init__(self, app_label=None, verbose=None, warn_only=None):
        if app_label:
            self.app_configs = [django_apps.get_app_config(app_label)]
        else:
            self.app_configs = django_apps.get_app_configs()
        self.verbose = verbose if verbose is not None else False
        self.warn_only = warn_only

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
        from edc_model import models as edc_models

        if issubclass(model, (edc_models.BaseUuidModel,)):
            permission_model_cls = django_apps.get_model("auth.permission")
            content_type_model_cls = django_apps.get_model("contenttypes.contenttype")
            if self.verbose:
                print(f"    - {model._meta.label_lower}")
            try:
                app_label, model_name = model._meta.label_lower.split(".")
                content_type = content_type_model_cls.objects.get(
                    app_label=app_label, model__iexact=model_name,
                )
            except ObjectDoesNotExist as e:
                if self.warn_only:
                    warn(f"ObjectDoesNotExist: {e} Got {model}.")
                else:
                    raise ObjectDoesNotExist(f"{e} Got {model}.")
            else:
                for action in ["import", "export"]:
                    codename = f"{action}_{model._meta.label_lower.split('.')[1]}"
                    opts = dict(content_type=content_type, codename=codename)
                    try:
                        obj = permission_model_cls.objects.get(**opts)
                    except ObjectDoesNotExist:
                        opts.update(name=f"Can {action} {model._meta.verbose_name}")
                        permission_model_cls.objects.create(**opts)
                        if self.verbose:
                            print(f"       created for {model._meta.label_lower}")
                    else:
                        obj.name = f"Can {action} {model._meta.verbose_name}"
                        obj.save()
