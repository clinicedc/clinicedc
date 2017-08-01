import sys

from django.apps import apps as django_apps
from django.core.management.color import color_style
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist


style = color_style()


class MetaformError(Exception):
    pass


class Metaform:

    """A class that gets the corresponding model instance, or not, for the
    given metadata object and sets it to itself along with other
    attributes like the visit, model class, metadata_obj, etc.
    """

    label = None

    def __init__(self, visit=None, metadata_obj=None, **kwargs):
        self.metadata_obj = metadata_obj
        self.visit = visit
        try:
            self.model_obj = self.model_cls.objects.get(**self.options)
        except AttributeError as e:
            if 'visit_model_attr' not in str(e):
                raise ImproperlyConfigured(f'{e} See {repr(self.model_cls)}')
            self.delete_invalid_metadata_obj(self.metadata_obj, exception=e)
            raise MetaformError()
        except ObjectDoesNotExist:
            self.model_obj = None

    def __repr__(self):
        return f'{self.__class__.__name__}({self.visit}, {self.metadata_obj})'

    @property
    def options(self):
        """Returns a dictionary of query options.
        """
        return {f'{self.model_cls.visit_model_attr()}': self.visit}

    @property
    def model_cls(self):
        """Returns a model class or raises.
        """
        try:
            model_cls = django_apps.get_model(self.metadata_obj.model)
        except LookupError as e:
            self.delete_invalid_metadata_obj(self.metadata_obj, exception=e)
            raise MetaformError()
        return model_cls

    def delete_invalid_metadata_obj(self, metadata_obj=None, exception=None):
        """Deletes the metadata object and prints a
        warning.
        """
        metadata_obj.delete()
        sys.stdout.write(style.NOTICE(
            f'\nDeleted invalid metadata. '
            f'{repr(metadata_obj)}.\nGot {exception}\n'))
        sys.stdout.flush()
