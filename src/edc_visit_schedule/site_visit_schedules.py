import copy
import sys

from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule

from edc_base.utils import get_utcnow

from .visit_schedule import VisitScheduleError


class RegistryNotLoaded(Exception):
    pass


class AlreadyRegisteredVisitSchedule(Exception):
    pass


class SiteVisitScheduleError(Exception):
    pass


class SiteVisitSchedules:

    """ Main controller of :class:`VisitSchedule` objects.

    A visit_schedule contains schedules
    """

    def __init__(self):
        self._registry = {}
        self.loaded = False

    @property
    def registry(self):
        if not self.loaded:
            raise RegistryNotLoaded(
                'Registry not loaded. Is AppConfig for \'edc_visit_schedule\' '
                'declared in settings?.')
        return self._registry

    @property
    def visit_schedules(self):
        return self.registry

    def register(self, visit_schedule):
        self.loaded = True
        if not visit_schedule.schedules:
            raise SiteVisitScheduleError(
                f'Visit schedule {visit_schedule} has no schedules. Add one before registering.')
        if visit_schedule.name not in self.registry:
            self.registry.update({visit_schedule.name: visit_schedule})
        else:
            raise AlreadyRegisteredVisitSchedule(
                'Visit Schedule {} is already registered.'.format(
                    visit_schedule))

    def get_visit_schedule(self, visit_schedule_name=None, **kwargs):
        """Returns a visit schedule instance or raises.
        """
        if not self.loaded:
            raise SiteVisitScheduleError('Registry is not loaded.')
        visit_schedule = None
        if visit_schedule_name:
            visit_schedule = self.registry.get(
                visit_schedule_name.split('.')[0])
            if not visit_schedule:
                keys = '\', \''.join(self.registry.keys())
                raise SiteVisitScheduleError(
                    f'Invalid visit schedule name. Got \'{visit_schedule_name}\'. '
                    f'Expected one of \'{keys}\'.')
        return visit_schedule

    def get_visit_schedules(self, visit_schedule_name=None, **kwargs):
        """Returns a dictionary of visit schedules.

        If visit_schedule_name not specified, returns all visit schedules.
        """
        if not self.loaded:
            raise SiteVisitScheduleError('Registry is not loaded.')
        if visit_schedule_name:
            visit_schedule_name = visit_schedule_name.split('.')[0]
            return dict(
                visit_schedule_name=self.get_visit_schedule(visit_schedule_name))
        else:
            return self.visit_schedules

    def get_schedule(self, model=None, visit_schedule_name=None,
                     schedule_name=None, **kwargs):
        """Returns a schedule or None; by name, meta.label_lower,
        model class or meta.visit_schedule_name.
        """
        if not self.loaded:
            raise SiteVisitScheduleError('Registry is not loaded.')
        schedule = None
        if not schedule_name:
            try:
                schedule_name = visit_schedule_name.split('.')[1]
            except (KeyError, AttributeError):
                pass
        for visit_schedule in self.get_visit_schedules(
                visit_schedule_name=visit_schedule_name).values():
            try:
                schedule = visit_schedule.get_schedule(
                    model=model, schedule_name=schedule_name)
            except VisitScheduleError:
                pass
            else:
                break
        return schedule

    def get_schedules(self, visit_schedule_name=None, schedule_name=None, **kwargs):
        """Returns a dictionary of schedules for this
        visit_schedule_name.
        """
        if not self.loaded:
            raise SiteVisitScheduleError('Registry is not loaded.')
        visit_schedule = self.get_visit_schedule(
            visit_schedule_name=visit_schedule_name)
        return visit_schedule.get_schedules(schedule_name=schedule_name)

    def get_visit_schedule_names(self):
        """Returns an ordered list of visit schedule names for
        this site.
        """
        visit_schedule_names = list(self.visit_schedules.keys())
        visit_schedule_names.sort()
        return visit_schedule_names

    def get_schedule_names(self, visit_schedule_names=None):
        """Returns an ordered list of schedule names for a given
        visit schedule name in visit_schedule_name.schedule_name
        dot format.
        """
        schedule_names = []
        if not isinstance(visit_schedule_names, (list, tuple)):
            visit_schedule_names = [visit_schedule_names]
        for visit_schedule_name in visit_schedule_names:
            schedule_names.extend(
                ['{}.{}'.format(visit_schedule_name, schedule_name)
                 for schedule_name in list(
                     self.get_visit_schedule(visit_schedule_name=visit_schedule_name).schedules.keys())])
        schedule_names.sort()
        return schedule_names

    def autodiscover(self, module_name=None, apps=None, verbose=None):
        """Autodiscovers classes in the visit_schedules.py file of
        any INSTALLED_APP.
        """
        module_name = module_name or 'visit_schedules'
        verbose = True if verbose is None else verbose
        if verbose:
            sys.stdout.write(
                f' * checking site for module \'{module_name}\' ...\n')
        for app in (apps or django_apps.app_configs):
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(
                        site_visit_schedules._registry)
                    import_module(f'{app}.{module_name}')
                    if verbose:
                        sys.stdout.write(
                            ' * registered visit schedule from application '
                            f'\'{app}\'\n')
                except Exception as e:
                    if f'No module named \'{app}.{module_name}\'' not in str(e):
                        raise SiteVisitScheduleError(
                            f'In module {app}.{module_name}: Got {e}') from e
                    site_visit_schedules._registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise SiteVisitScheduleError(
                            f'In module {app}.{module_name}: Got {e}') from e
            except ImportError:
                pass

    def validate(self):
        if not self.loaded:
            raise SiteVisitScheduleError('Registry is not loaded.')
        for visit_schedule in self.registry.values():
            for schedule in visit_schedule.schedules.values():
                schedule.visits.timepoint_dates(dt=get_utcnow())


site_visit_schedules = SiteVisitSchedules()
