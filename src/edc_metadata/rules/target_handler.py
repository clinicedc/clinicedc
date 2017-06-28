from django.apps import apps as django_apps


class TargetModelConflict(Exception):
    pass


class TargetModelMissingManagerMethod(Exception):
    pass


class TargetModelLookupError(Exception):
    pass


class TargetHandler:

    """A class that gets the target model "model instance"
    for a given visit, if it exists.

    The target model "model class" requires manager method `get_for_visit`.
    """

    def __init__(self, model=None, visit=None):
        self.visit = visit
        self.object = None
        if model == visit._meta.label_lower:
            raise TargetModelConflict(
                f'Target model and visit model are the same! '
                f'Got {model}=={visit._meta.label_lower}')
        try:
            self.model = django_apps.get_model(*model.split('.'))
        except LookupError as e:
            raise TargetModelLookupError(e)
        try:
            self.metadata_model = self.model().metadata_model
            self.object = self.model.objects.get_for_visit(
                self.visit)
        except self.model.DoesNotExist:
            pass
        except AttributeError as e:
            raise TargetModelMissingManagerMethod(
                f'Missing model manager method. '
                f'Target model=\'{model}\'. Got {e}')
