import copy
import sys

from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule

from edc_visit_schedule.exceptions import VisitScheduleError, RegistryNotLoaded, AlreadyRegistered
import sched
from django.core.exceptions import MultipleObjectsReturned


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
        name = name.split('.')[0]
        try:
            visit_schedule = self.registry[name]
        except KeyError:
            raise VisitScheduleError(
                'Invalid visit schedule name. Got \'{}\'. Possible names are [{}].'.format(
                    name, ', '.join(self.registry.keys())))
        return visit_schedule

    def get_visit_schedules(self):
        return self.registry

    def get_schedules(self, visit_schedule_name):
        return self.registry[visit_schedule_name].schedules

    def get_schedule(self, value=None):
        """Returns a schedule by name, meta.label_lower or meta.visit_schedule_name."""
        schedule = self.get_schedule_by_model(value)
        if not schedule:
            schedule = self.get_schedule_by_meta(visit_schedule_name=value)
        if not schedule:
            schedule = self.get_schedule_by_name(name=value)
        return schedule

    def get_schedule_by_name(self, name):
        """Lookup and return a schedule using a schedule name."""
        schedules = []
        for visit_schedule in self.registry.values():
            for schedule_name, schedule in visit_schedule.schedules.items():
                if name == schedule_name:
                    schedules.append(schedule)
        if len(schedules) > 1:
            raise MultipleObjectsReturned('More than one schedule returned for \'{}\'. Got {}.'.format(
                name, [s.name for s in schedules]))
        if schedules:
            return schedules[0]
        return None

    def get_schedule_by_meta(self, visit_schedule_name):
        """Lookup and return a schedule using the Meta visit_schedule_name."""
        try:
            visit_schedule_name, schedule_name = visit_schedule_name.split('.')
            schedule = self.get_visit_schedule(visit_schedule_name).schedules.get(schedule_name)
        except (ValueError, VisitScheduleError):
            schedule = None
        return schedule

    def get_schedule_by_model(self, value):
        """Lookup and return a schedule using the Meta label_lower."""
        try:
            model = django_apps.get_model(*value.split('.'))
        except (ValueError, AttributeError):
            model = value
        except LookupError:
            model = None
        try:
            visit_schedule_name, schedule_name = model._meta.visit_schedule_name.split('.')
            schedule = self.get_visit_schedule(visit_schedule_name).schedules.get(schedule_name)
        except (ValueError, AttributeError):
            schedule = None
        return schedule

    def get_visit_schedule_names(self):
        """Returns an ordered list of visit schedule names for this site."""
        visit_schedule_names = list(self.registry.keys())
        visit_schedule_names.sort()
        return visit_schedule_names

    def get_schedule_names(self, visit_schedule_name):
        """Returns an ordered list of schedule names for a given visit schedule name in
        visit_schedule_name.schedule_name dot format."""
        schedule_names = []
        if not isinstance(visit_schedule_name, (list, tuple)):
            visit_schedule_names = [visit_schedule_name]
        else:
            visit_schedule_names = visit_schedule_name
        for name in visit_schedule_names:
            schedule_names.extend(
                ['{}.{}'.format(name, schedule_name)
                 for schedule_name in list(self.get_visit_schedule(name).schedules.keys())])
        schedule_names.sort()
        return schedule_names

    def last_visit_datetime(self, subject_identifier, visit_schedule_name=None, schedule_name=None):
        """Returns the last visit datetime for a subject.

        Does not assume every visit schedule uses the same visit model."""
        last_visit_datetime = None
        if schedule_name and not visit_schedule_name:
            raise TypeError('Specify \'visit_schedule_name\' when specifying \'schedule_name\'. Got None')
        schedule_names = [] if not schedule_name else [schedule_name]
        visit_models = []
        max_visit_datetimes = []
        visit_schedule_names = [visit_schedule_name] if visit_schedule_name else self.get_visit_schedule_names()
        if not schedule_names:
            for visit_schedule_name in visit_schedule_names:
                schedule_names.extend(self.get_schedule_names(visit_schedule_name))
        for visit_schedule in [v for k, v in self.registry.items() if k in visit_schedule_names]:
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

    def enrollment(self, subject_identifier, visit_schedule_name, schedule_name):
        """Returns the enrollment instance for the given subject."""
        schedule = self.get_visit_schedule(visit_schedule_name).get_schedule(schedule_name)
        try:
            enrollment = schedule.enrollment_model.objects.get(
                subject_identifier=subject_identifier)
        except schedule.enrollment_model.DoesNotExist:
            enrollment = None
        return enrollment

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
