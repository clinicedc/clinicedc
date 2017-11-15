import sys
import copy

from django.apps import apps as django_apps
from django.core.management.color import color_style
from django.utils.module_loading import module_has_submodule
from importlib import import_module


class AlreadyRegistered(Exception):
    pass


class SiteProtocolSubjectsError(Exception):
    pass


class ProtocolSubjectCollection:

    """A class to contain a dictionary of protocol subjects.
    """

    def __init__(self):
        self.registry = {}

    def __repr__(self):
        return f'{self.__class__.__name__}()'

    def __len__(self):
        return len(self.registry.values())

    def __iter__(self):
        return iter(self.registry.values())

    def register(self, subject_type=None):
        name = subject_type.name
        model = subject_type.model
        key = self._key(name=name, model=model)
        if str(subject_type) != key:
            raise TypeError(
                f'{repr(subject_type)}. Got {subject_type.name} != {key}.')
        if key not in self.registry:
            self.registry.update({key: subject_type})
        else:
            raise AlreadyRegistered(
                f'Subject_type {key} is already registered.')

    def get(self, **kwargs):
        return self.registry.get(self._key(**kwargs))

    def _key(self, name=None, model=None):
        return f'{name}.{model}'

    def autodiscover(self, module_name=None, verbose=True):
        module_name = module_name or 'protocol_subjects'
        writer = sys.stdout.write if verbose else lambda x: x
        style = color_style()
        writer(f' * checking for site {module_name} ...\n')
        for app in django_apps.app_configs:
            writer(f' * searching {app}           \r')
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(
                        site_protocol_subjects.registry)
                    import_module(f'{app}.{module_name}')
                    writer(
                        f' * registered \'{module_name}\' from \'{app}\'\n')
                except SiteProtocolSubjectsError as e:
                    writer(f'   - loading {app}.{module_name} ... ')
                    writer(style.ERROR(f'ERROR! {e}\n'))
                except ImportError as e:
                    site_protocol_subjects.registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise SiteProtocolSubjectsError(str(e))
            except ImportError:
                pass
            except Exception as e:
                raise SiteProtocolSubjectsError(
                    f'{e.__class__.__name__} was raised when loading {module_name}. '
                    f'Got {e} See {app}.{module_name}')


site_protocol_subjects = ProtocolSubjectCollection()
