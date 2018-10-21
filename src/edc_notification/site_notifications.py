import copy
import sys

from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule


class AlreadyRegistered(Exception):
    pass


class RegistryNotLoaded(Exception):
    pass


class SiteNotifications:

    def __init__(self):
        self._registry = {}
        self.loaded = False

    def __repr__(self):
        return f'{self.__class__.__name__}(loaded={self.loaded})'

    @property
    def registry(self):
        if not self.loaded:
            raise RegistryNotLoaded(
                'Registry not loaded. Is AppConfig for \'edc_notification\' '
                'declared in settings?.')
        return self._registry

    def get(self, name):
        """Returns a Notification by name.
        """
        if not self.loaded:
            raise RegistryNotLoaded(self)
        return self._registry.get(name)

    def register(self, notification_cls=None):
        """Registers a Notification class.
        """
        if notification_cls:
            self.loaded = True
            if notification_cls.name not in self.registry:
                self.registry.update({notification_cls.name: notification_cls})
            else:
                raise AlreadyRegistered(
                    f'Notification {notification_cls.name} is already registered.')

    def notify(self, instance=None, created=None, user=None, **kwargs):
        """Notify for each class.
        """
        for notification_cls in self.registry.values():
            notification_cls().notify(instance=instance, created=created)

    def autodiscover(self, module_name=None, verbose=False):
        """Autodiscovers classes in the notifications.py file of any
        INSTALLED_APP.
        """
        module_name = module_name or 'notifications'
        verbose = True if verbose is None else verbose
        sys.stdout.write(f' * checking for {module_name} ...\n')
        for app in django_apps.app_configs:
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(
                        site_notifications._registry)
                    import_module(f'{app}.{module_name}')
                    if verbose:
                        sys.stdout.write(
                            f' * registered notifications from application \'{app}\'\n')
                except Exception as e:
                    if f'No module named \'{app}.{module_name}\'' not in str(e):
                        site_notifications._registry = before_import_registry
                        if module_has_submodule(mod, module_name):
                            raise
            except ModuleNotFoundError:
                pass


site_notifications = SiteNotifications()
