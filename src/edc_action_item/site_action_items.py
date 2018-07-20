import copy
import sys

from collections import OrderedDict
from django.apps import apps as django_apps
from django.core.management.color import color_style
from django.utils.module_loading import module_has_submodule
from edc_prn.prn import Prn
from edc_prn.site_prn_forms import site_prn_forms
from importlib import import_module


class AlreadyRegistered(Exception):
    pass


class SiteActionError(Exception):
    pass


class SiteActionItemCollection:

    populated_action_types = False

    def __init__(self):
        self.registry = OrderedDict()
        prn = Prn(
            model='edc_action_item.actionitem',
            url_namespace='edc_action_item_admin')
        site_prn_forms.register(prn)

    def __repr__(self):
        return f'{self.__class__.__name__}()'

    def __len__(self):
        return len(self.registry.values())

    def __iter__(self):
        return iter(self.registry.values())

    def register(self, action_cls=None):
        if action_cls.name in self.registry:
            raise AlreadyRegistered(
                f'Action class is already registered. Got name=\'{action_cls.name}\' '
                f'for {action_cls.__name__}')
        else:
            self.registry.update({action_cls.name: action_cls})
        if action_cls.show_link_to_changelist:
            prn = Prn(
                model=action_cls.reference_model,
                url_namespace=action_cls.admin_site_name)
            try:
                site_prn_forms.register(prn)
            except AlreadyRegistered:
                pass

    def get(self, name):
        """Returns an action class.
        """
        if name not in self.registry:
            raise SiteActionError(
                f'Action does not exist. Did you register the Action? '
                f'Expected one of {self.registry}. Got {name}.')
        # force create action type if it does not exist
        self.registry.get(name).action_type()
        return self.registry.get(name)

    def get_by_model(self, model=None):
        """Returns the action_cls linked to this reference model.
        """
        for action_cls in self.registry.values():
            if action_cls.reference_model == model:
                return self.get(action_cls.name)
        return None

    def get_show_link_to_add_actions(self):
        class Wrapper:
            def __init__(self, action_cls=None):
                self.name = action_cls.name
                self.display_name = action_cls.display_name
                self.action_type_id = str(action_cls.action_type().pk)
        names = [v.name for v in self.registry.values()
                 if v.show_link_to_add]
        return [Wrapper(action_cls=self.get(name)) for name in names]

    def populate_action_types(self):
        """Populates the ActionType model.

        Called by view.
        """
        if not self.populated_action_types:
            for action_cls in self.registry.values():
                action_cls.action_type()
        self.populated_action_types = True

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
                except SiteActionError as e:
                    writer(f'   - loading {app}.{module_name} ... ')
                    writer(style.ERROR(f'ERROR! {e}\n'))
                except ImportError as e:
                    site_action_items.registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise SiteActionError(str(e))
            except ImportError:
                pass
            except Exception as e:
                raise SiteActionError(
                    f'{e.__class__.__name__} was raised when loading {module_name}. '
                    f'Got {e} See {app}.{module_name}')


site_action_items = SiteActionItemCollection()
