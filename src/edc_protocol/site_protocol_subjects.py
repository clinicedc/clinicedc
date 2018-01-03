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


class SiteProtocolNotRegistered(Exception):
    pass


class ProtocolSubjectCollection:

    """A class to contain a dictionary of protocol subjects.
    """

    def __init__(self):
        self.registry = {}

    def __repr__(self):
        return f'{self.__class__.__name__}()'

    def register(self, subject_type=None):
        if subject_type.name not in self.registry:
            self.registry.update({subject_type.name: subject_type})
        else:
            raise AlreadyRegistered(
                f'Subject_type {subject_type.name} is already registered.')

    @property
    def subject_types(self):
        return self.registry

    def get(self, subject_type=None):
        return self.registry.get(subject_type)

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


site_protocol_subjects = ProtocolSubjectCollection()
