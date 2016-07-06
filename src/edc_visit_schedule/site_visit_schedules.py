import copy
import sys

from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule

from .exceptions import AlreadyRegistered


class Controller(object):

    """ Main controller of :class:`VisitScheduleConfiguration` objects. """

    def __init__(self):
        self.registry = {}

    def register(self, visit_schedule):
        if visit_schedule.name not in self.registry:
            self.registry.update({visit_schedule.name: visit_schedule})
        else:
            raise AlreadyRegistered('Visit Schedule {} is already registered.'.format(visit_schedule))

    def visit_schedules(self):
        """Returns the an ordered dictionary of visit_schedule_configurations"""
        return self.registry

    def get_visit_schedule(self, app_label, model_name):
        """Returns the visit_schedule for the given app_label."""
        visit_schedule = None
        for visit_schedule in self.registry.values():
            if visit_schedule.get_membership_forms(app_label, model_name):
                break
        return visit_schedule

    def get_visit_definition(self, schedule_name=None, code=None):
        schedule = self.get_schedule(schedule_name)
        return schedule.visit_definitions.get(code)

    def autodiscover(self, module_name=None):
        """Autodiscovers mapper classes in the visit_schedules.py file of any INSTALLED_APP."""
        module_name = module_name or 'visit_schedules'
        sys.stdout.write(' * checking for site {}s ...\n'.format(module_name))
        for app in django_apps.app_configs:
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(site_visit_schedules.registry)
                    import_module('{}.{}'.format(app, module_name))
                    sys.stdout.write(' * registered visit schedules \'{}\' from \'{}\'\n'.format(module_name, app))
                except:
                    site_visit_schedules.registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise
            except ImportError:
                pass

site_visit_schedules = Controller()
