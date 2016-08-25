import copy
import sys

from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule

from .exceptions import AlreadyRegistered


class Controller(object):

    """ Main controller of :class:`VisitSchedule` objects.

    A visit_schedule contains schedules"""

    def __init__(self):
        self.registry = {}

    def register(self, visit_schedule):
        if visit_schedule.name not in self.registry:
            self.registry.update({visit_schedule.name: visit_schedule})
        else:
            raise AlreadyRegistered('Visit Schedule {} is already registered.'.format(visit_schedule))

#     @property
#     def visit_schedules(self):
#         """Returns dictionary of visit_schedules"""
#         return self.registry

    def get_visit_schedule(self, name):
        return self.registry.get(name)

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
                    before_import_registry = copy.copy(site_visit_schedules.registry)
                    import_module('{}.{}'.format(app, module_name))
                    sys.stdout.write(' * registered visit schedules from application \'{}\'\n'.format(app))
                except:
                    site_visit_schedules.registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise
            except ImportError:
                pass

site_visit_schedules = Controller()
