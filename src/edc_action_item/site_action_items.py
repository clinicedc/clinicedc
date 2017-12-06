import copy
import sys

from collections import OrderedDict
from django.apps import apps as django_apps
from django.core.management.color import color_style
from django.utils.module_loading import module_has_submodule
from importlib import import_module


class AlreadyRegistered(Exception):
    pass


class SitePrnFormsError(Exception):
    pass


class SiteActionItemCollection:

    populated_action_type = False

    def __init__(self):
        self.registry = OrderedDict()

    def __repr__(self):
        return f'{self.__class__.__name__}()'

    def __len__(self):
        return len(self.registry.values())

    def __iter__(self):
        return iter(self.registry.values())

    def register(self, action_cls=None):
        if action_cls.name in self.registry:
            raise AlreadyRegistered(
                f'Action class is already registered. Got {action_cls}')
        else:
            self.registry.update({action_cls.name: action_cls})

    def populate_action_type(self):
        if not self.populated_action_type:
            for action_cls in self.registry.values():
                action_cls.action_type()
        self.populated_action_type = True

    def autodiscover(self, module_name=None, verbose=True):
        module_name = module_name or 'action_items'
        writer = sys.stdout.write if verbose else lambda x: x
        style = color_style()
        writer(f' * checking for site {module_name} ...\n')
        for app in django_apps.app_configs:
            writer(f' * searching {app}           \r')
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(
                        site_action_items.registry)
                    import_module(f'{app}.{module_name}')
                    writer(
                        f' * registered \'{module_name}\' from \'{app}\'\n')
                except SitePrnFormsError as e:
                    writer(f'   - loading {app}.{module_name} ... ')
                    writer(style.ERROR(f'ERROR! {e}\n'))
                except ImportError as e:
                    site_action_items.registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise SitePrnFormsError(str(e))
            except ImportError:
                pass
            except Exception as e:
                raise SitePrnFormsError(
                    f'{e.__class__.__name__} was raised when loading {module_name}. '
                    f'Got {e} See {app}.{module_name}')


site_action_items = SiteActionItemCollection()
