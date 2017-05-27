import copy
import sys

from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule

from .visit_schedule import SchedulesCollectionError


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

    def get_visit_schedule(self, visit_schedule_name=None):
        visit_schedule = None
        if visit_schedule_name:
            visit_schedule = self.registry.get(
                visit_schedule_name.split('.')[0])
            if not visit_schedule:
                visit_schedule_names = '\', \''.join(self.registry.keys())
                raise SiteVisitScheduleError(
                    f'Invalid visit schedule name. Got \'{visit_schedule_name}\'. '
                    f'Expected one of \'{visit_schedule_names}\'.')
        return visit_schedule

    def get_schedule(self, model=None, visit_schedule_name=None, schedule_name=None):
        """Returns a schedule by name, meta.label_lower or
        meta.visit_schedule_name.
        """
        schedule = None
        if model:
            schedule = self.get_schedule_by_model(model=model)
        elif visit_schedule_name:
            schedule = self.get_schedule_by_meta(
                visit_schedule_name=visit_schedule_name)
        elif schedule_name:
            schedule = self.get_schedule_by_name(
                schedule_name=schedule_name)
        return schedule

    def get_schedules(self, visit_schedule_name=None):
        """Returns a dictionary of schedules for this
        visit_schedule_name.
        """
        try:
            return self.registry[visit_schedule_name].schedules
        except KeyError as e:
            raise SiteVisitScheduleError(f'Invalid visit_schedule_name. Got {e}.') from e

    def get_schedule_by_name(self, schedule_name=None):
        """Lookup and return a schedule using a schedule name.
        """
        for visit_schedule in self.registry.values():
            schedule = visit_schedule.get_schedule(schedule_name=schedule_name)
            if schedule:
                return schedule
        return None

    def get_schedule_by_meta(self, visit_schedule_name=None):
        """Looks up and returns a schedule or None using the Meta
        visit_schedule_name.
        """
        _, schedule_name = visit_schedule_name.split('.')
        return self.get_schedule_by_name(schedule_name=schedule_name)

    def get_schedule_by_model(self, model=None):
        """Looks up and returns a schedule or None using the Meta label_lower.
        """
        for _, visit_schedule in self.registry.items():
            try:
                schedule = visit_schedule.get_schedule(model=model)
            except SchedulesCollectionError:
                pass
            else:
                if schedule:
                    return schedule
        return None

    def get_visit_schedule_names(self):
        """Returns an ordered list of visit schedule names for
        this site.
        """
        visit_schedule_names = list(self.registry.keys())
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

    def last_visit_datetime(self, subject_identifier,
                            visit_schedule_name=None, schedule_name=None):
        """Returns the last visit datetime for a subject.

        Does not assume every visit schedule uses the same visit model.
        """
        last_visit_datetime = None
        if schedule_name and not visit_schedule_name:
            raise TypeError(
                'Specify \'visit_schedule_name\' when specifying '
                '\'schedule_name\'. Got None')
        schedule_names = [] if not schedule_name else [schedule_name]
        visit_models = []
        max_visit_datetimes = []
        visit_schedule_names = ([
            visit_schedule_name]
            if visit_schedule_name else self.get_visit_schedule_names())
        if not schedule_names:
            for visit_schedule_name in visit_schedule_names:
                schedule_names.extend(
                    self.get_schedule_names(visit_schedule_name))
        for visit_schedule in [
                v for k, v in self.registry.items() if k in visit_schedule_names]:
            schedule_names = self.get_schedule_names(visit_schedule.name)
            if visit_schedule.visit_model not in visit_models:
                visit_models.append(visit_schedule.visit_model)
                last_visit = visit_schedule.visit_model.objects.last_visit(
                    subject_identifier=subject_identifier,
                    visit_schedule_names=visit_schedule_names,
                    schedule_names=schedule_names)
                if last_visit:
                    max_visit_datetimes.append(last_visit.report_datetime)
        if max_visit_datetimes:
            last_visit_datetime = max(max_visit_datetimes)
        return last_visit_datetime

    def enrollment(self, subject_identifier=None, visit_schedule_name=None, schedule_name=None):
        """Returns the enrollment instance for the given subject.
        """
        visit_schedule = self.get_visit_schedule(
            visit_schedule_name=visit_schedule_name)
        schedule = visit_schedule.get_schedule(schedule_name=schedule_name)
        model = schedule.enrollment_model
        try:
            obj = model.objects.get(
                subject_identifier=subject_identifier)
        except model.DoesNotExist:
            obj = None
        return obj

    def autodiscover(self, module_name=None):
        """Autodiscovers classes in the visit_schedules.py file of
        any INSTALLED_APP.
        """
        module_name = module_name or 'visit_schedules'
        sys.stdout.write(' * checking for site {}s ...\n'.format(module_name))
        for app in django_apps.app_configs:
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(
                        site_visit_schedules._registry)
                    import_module('{}.{}'.format(app, module_name))
                    sys.stdout.write(
                        ' * registered visit schedule from application '
                        '\'{}\'\n'.format(app))
                except Exception as e:
                    if f'No module named \'{app}.{module_name}\'' not in str(e):
                        raise SiteVisitScheduleError(f'In module {app}.{module_name}: Got {e}') from e
                    site_visit_schedules._registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise SiteVisitScheduleError(f'In module {app}.{module_name}: Got {e}') from e
            except ImportError:
                pass


site_visit_schedules = SiteVisitSchedules()
