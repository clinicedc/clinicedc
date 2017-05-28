from django.apps import apps as django_apps


def get_model(*args, model=None):
    """Returns the model class or None.
    """
    try:
        model._meta.label_lower
    except AttributeError as e:
        try:
            model = django_apps.get_model(*model.split('.'))
        except (LookupError, AttributeError, ValueError) as e:
            raise LookupError(f'Model=\'{model}\'. Got {e}.') from e
    return model
