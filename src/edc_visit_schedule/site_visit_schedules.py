import copy
import sys

from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule

from .visit_schedule_configuration import VisitScheduleConfiguration


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class Controller(object):

    """ Main controller of :class:`VisitScheduleConfiguration` objects. """

    def __init__(self):
        self.registry = {}

    def setregistry(self, visit_schedule_configuration):
        if not issubclass(visit_schedule_configuration, VisitScheduleConfiguration):
            raise AlreadyRegistered('Expected an instance of VisitScheduleConfiguration.')
        if visit_schedule_configuration.name not in self.registry:
            # register the instance
            self.registry.update({visit_schedule_configuration.name: visit_schedule_configuration()})
        else:
            raise AlreadyRegistered('Visit Schedule for name {0}.{1} '
                                    'is already registered.'.format(
                                        visit_schedule_configuration.app_label,
                                        visit_schedule_configuration.name))

    def get_visit_schedules(self):
        """Returns the an ordered dictionary of visit_schedule_configurations"""
        return self.registry

    def get_visit_schedule(self, app_label):
        """Returns the visit_schedule_configuration for the given app_label."""
        schedules = []
        for _, schedule in self.registry.items():
            if schedule.app_label == app_label:
                schedules.append(schedule)
        if len(schedules) == 1:
            return schedules[0]
        return schedules

    def build(self, app_label):
        visit_schedule = self.get_visit_schedule(self, app_label)
        if visit_schedule:
            visit_schedule.build()

    def build_all(self):
        for visit_schedule in self.get_visit_schedules().values():
            visit_schedule.build()

    def register(self, visit_schedule_configuration):
        """ Register visit_schedule_configurations"""
        self.setregistry(visit_schedule_configuration)

    def autodiscover(self, module_name=None):
        """Autodiscovers mapper classes in the mapper.py file of any INSTALLED_APP."""
        module_name = module_name or 'visit_schedule'
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
