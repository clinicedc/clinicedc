import copy

from django.apps import apps as django_apps
from django.conf import settings
try:
    from django.utils.importlib import import_module
except:
    from django.utils.module_loading import import_module
from django.utils.module_loading import module_has_submodule

from .visit_schedule_configuration import VisitScheduleConfiguration


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class Controller(object):

    """ Main controller of :class:`VisitScheduleConfiguration` objects. """

    def __init__(self):
        self._registry = {}

    def set_registry(self, visit_schedule_configuration):
        if not issubclass(visit_schedule_configuration, VisitScheduleConfiguration):
            raise AlreadyRegistered('Expected an instance of VisitScheduleConfiguration.')
        if visit_schedule_configuration.name not in self._registry:
            # register the instance
            self._registry.update({visit_schedule_configuration.name: visit_schedule_configuration()})
        else:
            raise AlreadyRegistered('Visit Schedule for name {0}.{1} '
                                    'is already registered.'.format(
                                        visit_schedule_configuration.app_label,
                                        visit_schedule_configuration.name))

    def get_visit_schedules(self):
        """Returns the an ordered dictionary of visit_schedule_configurations"""
        return self._registry

    def get_visit_schedule(self, app_label):
        """Returns the visit_schedule_configuration for the given app_label."""
        if app_label:
            if app_label in self._registry:
                return self._registry.get(app_label)
        return {}

    def build(self, app_label):
        visit_schedule = self.get_visit_schedule(self, app_label)
        if visit_schedule:
            visit_schedule.build()

    def build_all(self):
        for visit_schedule in self.get_visit_schedules().values():
            visit_schedule.build()

    def register(self, visit_schedule_configuration):
        """ Register visit_schedule_configurations"""
        self.set_registry(visit_schedule_configuration)

    def autodiscover(self):
        """ Autodiscover visit_schedule modules."""
        module_name = 'visit_schedule'
        before_import_registry = None
        for app in django_apps.app_configs:
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(site_visit_schedules.registry)
                    import_module('{}.{}'.format(app, module_name))
                    #sys.stdout.write(' * registered visit schedules from application \'{}\'\n'.format(app))
                except:
                    site_visit_schedules.registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise
            except ImportError:
                pass
        #for app in settings.INSTALLED_APPS:
        #    mod = import_module(app)
        #    try:
        #        before_import_registry = copy.copy(site_visit_schedules._registry)
        #        import_module('%s.visit_schedule' % app)
        #    except ImportError:
        #        site_visit_schedules._registry = before_import_registry
        #        if module_has_submodule(mod, 'visit_schedule'):
        #            raise

site_visit_schedules = Controller()
