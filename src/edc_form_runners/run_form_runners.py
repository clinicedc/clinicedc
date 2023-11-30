from django.apps import apps as django_apps

from .exceptions import (
    FormRunnerError,
    FormRunnerImproperlyConfigured,
    FormRunnerModelAdminNotFound,
)
from .get_form_runner import get_form_runner


def run_form_runners(
    app_labels: list[str] | None = None, model_names: list[str] | None = None
):
    model_names = model_names or []
    if app_labels:
        for app_config in django_apps.get_app_configs():
            if app_config.name in app_labels:
                for model_cls in app_config.get_models():
                    if not model_cls._meta.label_lower.split(".")[1].startswith("historical"):
                        model_names.append(model_cls._meta.label_lower)
    if not model_names:
        raise FormRunnerError("Nothing to do.")
    for model_name in model_names:
        print(model_name)
        try:
            get_form_runner(model_name, verbose=True).run_all()
        except (FormRunnerImproperlyConfigured, FormRunnerModelAdminNotFound) as e:
            print(f"{e} See {model_name}.")
        except AttributeError as e:
            print(f"{e} See {model_name}.")
