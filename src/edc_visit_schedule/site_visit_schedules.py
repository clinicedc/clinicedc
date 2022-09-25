from __future__ import annotations

import copy
import sys
from typing import TYPE_CHECKING, Tuple

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.utils.module_loading import import_module, module_has_submodule

if TYPE_CHECKING:
    from .models import VisitSchedule as VisitScheduleModel
    from .schedule import Schedule
    from .visit_schedule import VisitSchedule


class RegistryNotLoaded(Exception):
    pass


class AlreadyRegisteredVisitSchedule(Exception):
    pass


class SiteVisitScheduleError(Exception):
    pass


class SiteVisitSchedules:
    """Main controller of :class:`VisitSchedule` objects.

    A visit_schedule contains schedules
    """

    def __init__(self):
        self._registry: dict = {}
        self._all_post_consent_models: dict[str, str] | None = None
        self.loaded: bool = False

    @property
    def registry(self) -> dict[str, VisitSchedule]:
        if not self.loaded:
            raise RegistryNotLoaded(
                "Registry not loaded. Is AppConfig for 'edc_visit_schedule' "
                "declared in settings?."
            )
        return self._registry

    def register(self, visit_schedule: VisitSchedule) -> None:
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
        self.get_offstudy_model()

    @property
    def visit_schedules(self) -> dict[str, VisitSchedule]:
        return self.registry

    def get_visit_schedule(self, visit_schedule_name=None) -> VisitSchedule:
        """Returns a visit schedule instance or raises."""
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

    def get_visit_schedules(self, *visit_schedule_names) -> dict[str, VisitSchedule]:
        """Returns a dictionary of visit schedules.

        If visit_schedule_name not specified, returns all visit schedules.
        """
        visit_schedules = {}
        for visit_schedule_name in visit_schedule_names:
            try:
                visit_schedule_name = visit_schedule_name.split(".")[0]
            except AttributeError:
                pass
            visit_schedules[visit_schedule_name] = self.get_visit_schedule(visit_schedule_name)
        return visit_schedules or self.registry

    def get_by_onschedule_model(self, onschedule_model=None) -> Tuple[VisitSchedule, Schedule]:
        """Returns a tuple of (visit_schedule, schedule)
        for the given onschedule model.

        attr `onschedule_model` is in "label_lower" format.
        """
        return self.get_by_model(attr="onschedule_model", model=onschedule_model)

    def get_by_offschedule_model(
        self, offschedule_model=None
    ) -> Tuple[VisitSchedule, Schedule]:
        """Returns a tuple of visit_schedule, schedule
        for the given offschedule model.

        attr `offschedule_model` is in "label_lower" format.
        """
        return self.get_by_model(attr="offschedule_model", model=offschedule_model)

    def get_by_loss_to_followup_model(
        self, loss_to_followup_model=None
    ) -> Tuple[VisitSchedule, Schedule]:
        """Returns a tuple of visit_schedule, schedule
        for the given loss_to_followup model.

        attr `loss_to_followup_model` is in "label_lower" format.
        """
        return self.get_by_model(attr="loss_to_followup_model", model=loss_to_followup_model)

    def get_by_model(
        self, attr: str = None, model: str = None
    ) -> Tuple[VisitSchedule, Schedule]:
        ret = []
        for visit_schedule in self.visit_schedules.values():
            for schedule in visit_schedule.schedules.values():
                try:
                    model_name = getattr(schedule, attr)
                except (AttributeError, TypeError):
                    raise SiteVisitScheduleError(
                        f"Invalid attr for Schedule. See {schedule}. Got {attr}."
                    )
                if model_name and model_name == model:
                    ret.append([visit_schedule, schedule])
        if not ret:
            raise SiteVisitScheduleError(
                f"Schedule not found. No schedule exists for {attr}={model}."
            )
        elif len(ret) > 1:
            raise SiteVisitScheduleError(
                f"Schedule is ambiguous. More than one schedule exists for "
                f"{attr}={model}. Got {ret}"
            )
        visit_schedule, schedule = ret[0]
        return visit_schedule, schedule

    def get_by_offstudy_model(self, offstudy_model=None) -> list[VisitSchedule]:
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

    def get_consent_model(self, visit_schedule_name: str, schedule_name: str) -> str:
        """Returns the consent model name"""
        schedule = self.get_visit_schedule(visit_schedule_name).schedules.get(schedule_name)
        return schedule.consent_model

    def get_onschedule_model(self, visit_schedule_name: str, schedule_name: str) -> str:
        """Returns the onschedule model name"""
        schedule = self.get_visit_schedule(visit_schedule_name).schedules.get(schedule_name)
        return schedule.onschedule_model

    @staticmethod
    def get_offstudy_model() -> str:
        offstudy_models = []
        for _, visit_schedule in site_visit_schedules.get_visit_schedules().items():
            if visit_schedule.offstudy_model not in offstudy_models:
                offstudy_models.append(visit_schedule.offstudy_model)
        if len(offstudy_models) > 1:
            raise SiteVisitScheduleError(
                "More than one off study model defined. See visit schedules. "
                f"Got {offstudy_models}."
            )
        if len(offstudy_models) == 0:
            visit_schedule_names = [
                k for k, v in site_visit_schedules.get_visit_schedules().items()
            ]
            raise SiteVisitScheduleError(
                "No off study model defined in visit_schedule. "
                f"Got registered visit_schedules: {visit_schedule_names}."
            )
        offstudy_model = offstudy_models[0]
        return offstudy_model

    @property
    def all_post_consent_models(self) -> dict[str, str]:
        """Returns a dictionary of models that require consent before save.

        {model_name1: consent_model_name, model_name2: consent_model_name, ...}
        """
        if not self._all_post_consent_models:
            models = {}
            for visit_schedule in self.visit_schedules.values():
                models.update(**visit_schedule.all_post_consent_models)
            self._all_post_consent_models = models
        return self._all_post_consent_models

    def check(self) -> dict[str, list]:
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

    @staticmethod
    def to_model(model_cls: VisitScheduleModel) -> None:
        """Updates the VisitSchedule model with the current visit
        schedule, schedule and visits.

        Note: The VisitSchedule model is just for reference and does
        not replace information gathered from -this- class.

        Note: in addition to other attrs, such as visit code,
        timepoint must be unique across all schedules. Timepoint
        will not be updated for an existing record and may raise
        an integrity error. If you change a timepoint value within
        an existing schedule, you may need to change it manually via
        the database client.
        """
        model_cls.objects.update(active=False)
        for visit_schedule in site_visit_schedules.visit_schedules.values():
            for schedule in visit_schedule.schedules.values():
                for visit in schedule.visits.values():
                    opts = dict(
                        visit_schedule_name=visit_schedule.name,
                        schedule_name=schedule.name,
                        visit_code=visit.code,
                        visit_name=visit.name,
                        visit_title=visit.title,
                        timepoint=visit.timepoint,
                        active=True,
                    )
                    try:
                        obj = model_cls.objects.get(
                            visit_schedule_name=visit_schedule.name,
                            schedule_name=schedule.name,
                            timepoint=visit.timepoint,
                        )
                    except ObjectDoesNotExist:
                        model_cls.objects.create(**opts)
                    else:
                        for fld, value in opts.items():
                            setattr(obj, fld, value)
                        obj.save()

    def autodiscover(self, module_name=None, apps=None, verbose=None) -> None:
        """Autodiscovers classes in the visit_schedules.py file of
        any INSTALLED_APP.
        """
        self.loaded = True
        before_import_registry = None
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
                        sys.stdout.write(" * registered visit schedule from " f"'{app}'\n")
                except Exception as e:
                    if f"No module named '{app}.{module_name}'" not in str(e):
                        raise
                    site_visit_schedules._registry = before_import_registry
                    if module_has_submodule(mod, module_name):
                        raise
            except ModuleNotFoundError:
                pass


site_visit_schedules = SiteVisitSchedules()
