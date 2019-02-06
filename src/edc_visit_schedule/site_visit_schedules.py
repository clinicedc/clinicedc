import copy
import sys

from django.apps import apps as django_apps
from django.utils.module_loading import import_module, module_has_submodule


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
        self._all_post_consent_models = None
        self.loaded = False

    @property
    def registry(self):
        if not self.loaded:
            raise RegistryNotLoaded(
                "Registry not loaded. Is AppConfig for 'edc_visit_schedule' "
                "declared in settings?."
            )
        return self._registry

    def register(self, visit_schedule):
        self.loaded = True
        if not visit_schedule.schedules:
            raise SiteVisitScheduleError(
                f"Visit schedule {visit_schedule} has no schedules. "
                f"Add one before registering."
            )
        if visit_schedule.name not in self.registry:
            self.registry.update({visit_schedule.name: visit_schedule})
        else:
            raise AlreadyRegisteredVisitSchedule(
                f"Visit Schedule {visit_schedule} is already registered."
            )
        self._all_post_consent_models = None

    @property
    def visit_schedules(self):
        return self.registry

    def get_visit_schedule(self, visit_schedule_name=None, **kwargs):
        """Returns a visit schedule instance or raises.
        """
        try:
            visit_schedule_name = visit_schedule_name.split(".")[0]
        except AttributeError:
            pass
        visit_schedule = self.registry.get(visit_schedule_name)
        if not visit_schedule:
            visit_schedule_names = "', '".join(self.registry.keys())
            raise SiteVisitScheduleError(
                f"Invalid visit schedule name. Got '{visit_schedule_name}'. "
                f"Expected one of '{visit_schedule_names}'. See {repr(self)}."
            )
        return visit_schedule

    def get_visit_schedules(self, *visit_schedule_names):
        """Returns a dictionary of visit schedules.

        If visit_schedule_name not specified, returns all visit schedules.
        """
        visit_schedules = {}
        for visit_schedule_name in visit_schedule_names:
            try:
                visit_schedule_name = visit_schedule_name.split(".")[0]
            except AttributeError:
                pass
            visit_schedules[visit_schedule_name] = self.get_visit_schedule(
                visit_schedule_name
            )
        return visit_schedules or self.registry

    def get_by_onschedule_model(self, onschedule_model=None):
        """Returns a tuple of (visit_schedule, schedule)
        for the given onschedule model.

        attr `onschedule_model` is in "label_lower" format.
        """
        schedule = None
        for visit_schedule in self.visit_schedules.values():
            for schedule in visit_schedule.schedules.values():
                if schedule.onschedule_model == onschedule_model:
                    return visit_schedule, schedule
        raise SiteVisitScheduleError(
            f"Schedule not found. No schedule exists for "
            f"onschedule_model={onschedule_model}."
        )
        return None

    def get_by_offschedule_model(self, offschedule_model=None):
        """Returns a tuple of visit_schedule, schedule
        for the given offschedule model.
        """
        for visit_schedule in self.visit_schedules.values():
            for schedule in visit_schedule.schedules.values():
                if schedule.offschedule_model == offschedule_model:
                    return visit_schedule, schedule
        raise SiteVisitScheduleError(
            f"Schedule not found. No schedule exists for "
            f"offschedule_model={offschedule_model}."
        )
        return None, None

    def get_by_offstudy_model(self, offstudy_model=None):
        """Returns a list of visit_schedules for the given
        offstudy model.
        """
        visit_schedules = []
        for visit_schedule in self.visit_schedules.values():
            if visit_schedule.offstudy_model == offstudy_model:
                visit_schedules.append(visit_schedule)
        if not visit_schedules:
            raise SiteVisitScheduleError(
                f"No visit schedules have been defined using the "
                f"offstudy model '{offstudy_model}'"
            )
        return visit_schedules

    @property
    def all_post_consent_models(self):
        """Returns a list of models that require consent before save.
        """
        if not self._all_post_consent_models:
            models = {}
            for visit_schedule in self.visit_schedules.values():
                models.update(**visit_schedule.all_post_consent_models)
            self._all_post_consent_models = models
        return self._all_post_consent_models

    def check(self):
        if not self.loaded:
            raise SiteVisitScheduleError("Registry is not loaded.")
        errors = {"visit_schedules": [], "schedules": [], "visits": []}
        for visit_schedule in site_visit_schedules.visit_schedules.values():
            errors["visit_schedules"].extend(visit_schedule.check())
            for schedule in visit_schedule.schedules.values():
                errors["schedules"].extend(schedule.check())
                for visit in schedule.visits.values():
                    errors["visits"].extend(visit.check())
        return errors

    def autodiscover(self, module_name=None, apps=None, verbose=None):
        """Autodiscovers classes in the visit_schedules.py file of
        any INSTALLED_APP.
        """
        self.loaded = True
        module_name = module_name or "visit_schedules"
        verbose = True if verbose is None else verbose
        if verbose:
            sys.stdout.write(f" * checking site for module '{module_name}' ...\n")
        for app in apps or django_apps.app_configs:
            try:
                mod = import_module(app)
                try:
                    before_import_registry = copy.copy(site_visit_schedules._registry)
                    import_module(f"{app}.{module_name}")
                    if verbose:
                        sys.stdout.write(
                            " * registered visit schedule from " f"'{app}'\n"
                        )
                except Exception as e:
                    if f"No module named '{app}.{module_name}'" not in str(e):
                        raise
                    site_visit_schedules._registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise
            except ModuleNotFoundError:
                pass


site_visit_schedules = SiteVisitSchedules()
