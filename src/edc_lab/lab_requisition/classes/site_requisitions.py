import copy
from django.conf import settings
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass

# TODO: is this used??.


class SiteRequisitions(object):
    """Registers requisition models from modules with a requisitions module (requisitions.py)."""
    def __init__(self):
        self._registry = {}

    def register(self, subject_type, requisition):
        if subject_type in self._registry.iterkeys():
            raise AlreadyRegistered('The requisition for {0} is already registered' % subject_type)
        self._registry.update({subject_type: requisition})

    def all(self):
        return self._registry

    def get(self, subject_type):
        return self._registry.get(subject_type, None)

    def autodiscover(self):
        """Searches all apps for :file:`requisitions.py."""
        for app in settings.INSTALLED_APPS:
            mod = import_module(app)
            try:
                before_import_registry = copy.copy(site_requisitions._registry)
                import_module('%s.requisitions' % app)
            except:
                site_requisitions._registry = before_import_registry
                if module_has_submodule(mod, 'requisitions'):
                    raise
# A global to contain all requisition classes from modules
site_requisitions = SiteRequisitions()
