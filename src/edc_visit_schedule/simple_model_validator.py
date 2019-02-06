from django.apps import apps as django_apps


class InvalidModel(Exception):
    pass


class SimpleModelValidator:
    """Validate label lower without loading the model.

    Does not validate the model_name other than it cannot be None.
    """

    def __init__(self, model=None, attr=None):
        try:
            app_label, _ = model.split(".")
        except AttributeError:
            raise InvalidModel(
                f"Invalid label lower format for '{attr}'. " f"Got {model}"
            )
        else:
            app_labels = [
                app_config.name for app_config in django_apps.get_app_configs()
            ]
            if app_label not in app_labels:
                raise InvalidModel(
                    f"Invalid model. app_label does not exist for "
                    f"'{attr}'. Got {model}"
                )
