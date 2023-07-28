import json
import re

from django.apps import apps as django_apps
from edc_locator.utils import LocatorModelError, get_locator_model
from edc_offstudy.utils import get_offstudy_model
from edc_visit_tracking.constants import MISSED_VISIT, SCHEDULED, UNSCHEDULED
from edc_visit_tracking.utils import get_related_visit_model

from .schedules_collection import SchedulesCollection


class VisitScheduleError(Exception):
    pass


class VisitScheduleNameError(Exception):
    pass


class VisitScheduleSiteError(Exception):
    pass


class VisitScheduleAppointmentModelError(Exception):
    pass


class AlreadyRegisteredSchedule(Exception):
    pass


class VisitSchedule:
    name_regex = r"[a-z0-9\_\-]+$"
    name_regex_msg = "numbers, lower case letters and '_'"
    schedules_collection = SchedulesCollection
    create_metadata_on_reasons = [SCHEDULED, UNSCHEDULED, MISSED_VISIT]
    delete_metadata_on_reasons = []

    def __init__(
        self,
        name=None,
        verbose_name=None,
        previous_visit_schedule=None,
        death_report_model=None,
        offstudy_model=None,
        locator_model=None,
        visit_model=None,
        visit_model_reason_field=None,
        create_metadata_on_reasons=None,
        delete_metadata_on_reasons=None,
    ):
        self._all_post_consent_models = None
        self.name = name
        self.schedules = self.schedules_collection(visit_schedule_name=name)
        self.offstudy_model = offstudy_model or get_offstudy_model()
        self.death_report_model = death_report_model

        if locator_model and locator_model != get_locator_model():
            raise LocatorModelError(
                f"Ambiguous Locator model. See settings.SUBJECT_LOCATOR_MODEL and "
                f"{self.name}. Got `{get_locator_model()}` from "
                f"settings and `{locator_model}` from {self.name}."
            )
        self.locator_model = locator_model or get_locator_model()

        self.previous_visit_schedule = previous_visit_schedule
        self.visit_model = visit_model or get_related_visit_model()
        self.visit_model_reason_field = visit_model_reason_field or "reason"
        self.create_metadata_on_reasons = (
            create_metadata_on_reasons or self.create_metadata_on_reasons
        )
        self.delete_metadata_on_reasons = (
            delete_metadata_on_reasons or self.delete_metadata_on_reasons
        )

        if not re.match(self.name_regex, name):
            raise VisitScheduleNameError(
                f"Visit schedule name may only contain {self.name_regex_msg}. Got {name}"
            )
        self.title = self.verbose_name = verbose_name or " ".join(
            [s.capitalize() for s in name.split("_")]
        )

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.name}')"

    def __str__(self):
        return self.name

    @property
    def offstudy_model_cls(self):
        return django_apps.get_model(self.offstudy_model)

    @property
    def locator_model_cls(self):
        return django_apps.get_model(self.locator_model)

    @property
    def death_report_model_cls(self):
        return django_apps.get_model(self.death_report_model)

    def add_schedule(self, schedule=None):
        """Adds a schedule, if not already added."""
        if schedule.name in self.schedules:
            raise AlreadyRegisteredSchedule(
                f"Schedule '{schedule.name}' is already registered. See '{self}'"
            )
        self.schedules.update({schedule.name: schedule})
        self._all_post_consent_models = None
        return schedule

    def check(self):
        warnings = []
        for model in [
            "death_report",
            "locator",
            "offstudy",
        ]:
            try:
                getattr(self, f"{model}_model_cls")
            except LookupError as e:
                warnings.append(f"{e} See visit schedule '{self.name}'.")
        return warnings

    @property
    def all_post_consent_models(self):
        """Returns a dictionary of models and the needed consent
        model.

        These models may only be complete after the consent model.

        {model_name1:
            consent_model_name, model_name2:
                consent_model_name, ...}
        """
        if not self._all_post_consent_models:
            models = {}
            models.update({self.offstudy_model: None})
            models.update({self.death_report_model: None})
            models.update({self.locator_model: None})
            for schedule in self.schedules.values():
                models.update({schedule.onschedule_model: schedule.consent_model})
                models.update({schedule.offschedule_model: schedule.consent_model})
                for visit in schedule.visits.values():
                    for crf in visit.forms:
                        models.update({crf.model: schedule.consent_model})
                    for crf in visit.unscheduled_forms:
                        models.update({crf.model: schedule.consent_model})
            if None in (list(models.keys())):
                raise VisitScheduleError(
                    "One or more required models has not been defined. "
                    f"Check the declaration for visit schedule '{self}'. "
                    f"Got {models}."
                )
            self._all_post_consent_models = models
        return self._all_post_consent_models

    def to_dict(self):
        return {k: v.to_dict() for k, v in self.schedules.items()}

    def to_json(self):
        """Returns a json representation of the visit schedule.

        For example, list all required CRF model names for
        visit 1000:

            json_str = visit_schedule.to_json()
            model_names = [
                crf[0] for crf in json.loads(json_str).get(
                    'schedule').get('1000').get('crfs')
                if crf[1]]
        """
        return json.dumps(self.to_dict())
