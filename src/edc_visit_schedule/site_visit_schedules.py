import copy
import sys

from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule

from edc_visit_schedule.exceptions import VisitScheduleError, RegistryNotLoaded, AlreadyRegistered


class SiteVisitSchedules:

    """ Main controller of :class:`VisitSchedule` objects.

    A visit_schedule contains schedules"""

    def __init__(self):
        self._registry = {}
        self.loaded = False

    @property
    def registry(self):
        if not self.loaded:
            raise RegistryNotLoaded(
                'Registry not loaded. Is AppConfig for \'edc_visit_schedule\' declared in settings?.')
        return self._registry

    def register(self, visit_schedule):
        self.loaded = True
        if visit_schedule.name not in self.registry:
            self.registry.update({visit_schedule.name: visit_schedule})
        else:
            raise AlreadyRegistered('Visit Schedule {} is already registered.'.format(visit_schedule))

    def get_visit_schedule(self, name):
        try:
            visit_schedule = self.registry[name]
        except KeyError:
            raise VisitScheduleError(
                'Invalid visit schedule name. Got \'{}\'. Possible names are [{}].'.format(
                    name, ', '.join(self.registry.keys())))
        return visit_schedule

    def get_schedule(self, value=None):
        """Returns the a schedule for the given enrollment model."""
        schedule = None
        for visit_schedule in self.registry.values():
            schedule = visit_schedule.get_schedule(value)
            if schedule:
                break
        return schedule

    def autodiscover(self, module_name=None):
        """Autodiscovers classes in the visit_schedules.py file of any INSTALLED_APP."""
        module_name = module_name or 'visit_schedules'
        sys.stdout.write(' * checking for site {}s ...\n'.format(module_name))
        for app in django_apps.app_configs:
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(site_visit_schedules._registry)
                    import_module('{}.{}'.format(app, module_name))
                    sys.stdout.write(' * registered visit schedule from application \'{}\'\n'.format(app))
                except Exception as e:
                    if 'No module named \'{}.{}\''.format(app, module_name) not in str(e):
                        raise Exception(e)
                    site_visit_schedules._registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise
            except ImportError:
                pass

site_visit_schedules = SiteVisitSchedules()
