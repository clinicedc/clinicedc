from django.apps import apps as django_apps


class GetModelError(Exception):
    pass


class GetModelCls:

    """A class to get the requisition model based on label_lower
    or a model class.

    This is needed so that the call to get_model is after the
    Apps registry has loaded.
    """

    def __init__(self, model=None):
        try:
            self.model_name = model._meta.label_lower
        except AttributeError:
            self._model = None
            self.model_name = model
        else:
            self._model = model

    def get_model(self):
        if not self._model:
            try:
                self._model = django_apps.get_model(self.model_name)
            except (AttributeError, ValueError) as e:
                raise GetModelError(
                    f'Invalid model name \'{self.model_name}\'. Got {e}') from e
            except LookupError as e:
                raise GetModelError(
                    f'Invalid model \'{self.model_name}\'. Got {e}') from e
        return self._model
