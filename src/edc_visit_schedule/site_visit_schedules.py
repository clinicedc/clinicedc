import copy
import sys

from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule

from .exceptions import AlreadyRegistered


class Controller(object):

    """ Main controller of :class:`VisitSchedule` objects. """

    def __init__(self):
        self.registry = {}

    def register(self, visit_schedule):
        if visit_schedule.name not in self.registry:
            self.registry.update({visit_schedule.name: visit_schedule})
        else:
            raise AlreadyRegistered('Visit Schedule {} is already registered.'.format(visit_schedule))

    @property
    def visit_schedules(self):
        """Returns dictionary of visit_schedules"""
        return self.registry

    def get_visit_schedule(self, app_label=None, model_name=None, schedule_name=None, model=None):
        """Returns the visit_schedule for the given app_label, model_name or schedule_name."""
        visit_schedule = None
        if schedule_name:
            for visit_schedule in self.registry.values():
                if visit_schedule.schedules(schedule_name):
                    break
        else:
            if model:
                app_label = model._meta.app_label
                model_name = model._meta.model_name
            for visit_schedule in self.registry.values():
                if visit_schedule.get_membership_form(app_label, model_name):
                    break
        return visit_schedule

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
                    sys.stdout.write(' * registered visit schedules from application \'{}\'\n'.format(app))
                except:
                    site_visit_schedules.registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise
            except ImportError:
                pass

site_visit_schedules = Controller()
