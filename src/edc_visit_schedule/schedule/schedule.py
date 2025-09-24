from __future__ import annotations

import re
from copy import deepcopy
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from django.apps import apps as django_apps

from edc_consent.consent_definition import ConsentDefinition
from edc_consent.exceptions import (
    ConsentDefinitionDoesNotExist,
    ConsentDefinitionValidityPeriodError,
)
from edc_registration import get_registered_subject_model_cls
from edc_sites import site_sites
from edc_sites.single_site import SingleSite
from edc_utils import formatted_date

from ..exceptions import NotOnScheduleError, NotOnScheduleForDateError
from ..site_visit_schedules import site_visit_schedules
from ..subject_schedule import SubjectSchedule
from ..visit import Visit
from .visit_collection import VisitCollection
from .window import Window

if TYPE_CHECKING:
    from edc_appointment.models import Appointment
    from edc_model.models import BaseUuidModel
    from edc_sites.model_mixins import SiteModelMixin
    from edc_visit_tracking.model_mixins import VisitModelMixin as Base

    from ..models import OffSchedule, OnSchedule, SubjectScheduleHistory

    class RelatedVisitModel(SiteModelMixin, Base, BaseUuidModel):
        pass


class ScheduleError(Exception):
    pass


class ScheduleNameError(Exception):
    pass


class AlreadyRegisteredVisit(Exception):  # noqa: N818
    pass


class VisitTimepointError(Exception):
    pass


class Schedule:
    """A class that represents a "schedule" of visits.

    Is contained by a "visit schedule".

    Contains an ordered dictionary of visit instances and the onschedule
    and offschedule models used to get on and off the schedule.
    """

    name_regex = r"[a-z0-9\_\-]+$"
    visit_cls = Visit
    visit_collection_cls: type[VisitCollection] = VisitCollection
    window_cls = Window

    def __init__(
        self,
        name: str,
        onschedule_model: str,
        offschedule_model: str,
        consent_definitions: list[ConsentDefinition] | ConsentDefinition = None,
        loss_to_followup_model: str | None = None,
        appointment_model: str | None = None,
        offstudymedication_model: str | None = None,
        history_model: str | None = None,
        verbose_name: str | None = None,
        sequence: str | None = None,
        base_timepoint: float | Decimal | None = None,
    ):
        self._consent_definitions = None
        if not name or not re.match(r"[a-z0-9_\-]+$", name):
            raise ScheduleNameError(
                f"Invalid name. Got '{name}'. May only contains numbers, "
                "lower case letters and '_'."
            )
        self.name = name

        self.consent_definitions = consent_definitions

        if isinstance(base_timepoint, (float,)):
            base_timepoint = Decimal(str(base_timepoint))
        elif isinstance(base_timepoint, (int,)):
            base_timepoint = Decimal(str(base_timepoint) + ".0")
        self._visits = self.visit_collection_cls()
        self.base_timepoint = base_timepoint or Decimal("0.0")
        self.verbose_name = verbose_name or name
        self.sequence = sequence or name
        self.appointment_model: str = appointment_model or "edc_appointment.appointment"
        self.offschedule_model: str = offschedule_model.lower()
        self.onschedule_model: str = onschedule_model.lower()
        self.loss_to_followup_model = (
            None if loss_to_followup_model is None else loss_to_followup_model.lower()
        )
        self.offstudymedication_model = (
            None if offstudymedication_model is None else offstudymedication_model.lower()
        )
        self.history_model = history_model or "edc_visit_schedule.subjectschedulehistory"

    def __repr__(self):
        return f"Schedule({self.name})"

    def __str__(self):
        return self.name

    @property
    def consent_definitions(self) -> list[ConsentDefinition]:
        return self._consent_definitions

    @consent_definitions.setter
    def consent_definitions(
        self, consent_definitions: list[ConsentDefinition] | ConsentDefinition
    ):
        if isinstance(consent_definitions, (ConsentDefinition,)):
            self._consent_definitions: list[ConsentDefinition] = [consent_definitions]
        else:
            self._consent_definitions: list[ConsentDefinition] = [
                x for x in consent_definitions if x
            ]
        if not self._consent_definitions:
            raise ScheduleError(
                f"ConsentDefinition(s) may not be None. See Schedule `{self}`. "
                f"Got `{consent_definitions}`."
            )
        self._consent_definitions = sorted(self._consent_definitions, key=lambda x: x.version)

    @property
    def visits(self) -> VisitCollection:
        """Returns an unfiltered dictionary of visits in this
        schedule.
        """
        return self._visits

    def visits_for_subject(
        self,
        subject_identifier: str,
        report_datetime: datetime,
        site_id: int | None = None,
        consent_definition: ConsentDefinition | None = None,
    ) -> VisitCollection:
        """Returns a deep copy of visits collection filtered for a
        given consented subject.

        If not consented, returns an empty visit collection.

        Check if the consent definition `extended_by` attribute is
        set. If set, visits/timepoints listed with the extended
        consent definition's `timepoints` are EXCLUDED if the subject
        has NOT completed the consent definition extension model.
        """
        visits = self.visit_collection_cls()
        cdef = self.get_consent_definition(
            report_datetime=report_datetime,
            site=site_sites.get(site_id),
            consent_definition=consent_definition,
        )
        if cdef.get_consent_for(subject_identifier=subject_identifier, site_id=site_id):
            visits = deepcopy(self.visits)
            if cdef.extended_by:
                visits = cdef.extended_by.update_visit_collection(
                    visits,
                    subject_identifier,
                    site_id,
                    original_visit_collection=self.visits,
                )
        return visits

    def add_visit(self, visit=None, **kwargs) -> Visit:
        """Adds a unique visit to the schedule.

        Called when first declaring the schedule at bootup.
        """
        visit = visit or self.visit_cls(**kwargs)
        if visit.timepoint < self.base_timepoint:
            raise VisitTimepointError(
                "Visit timepoint cannot be less than this schedule's base_timepoint. "
                f"See {visit}. Got visit.timepoint={visit.timepoint}."
            )

        for attr in ["code", "title", "timepoint", "rbase"]:
            if getattr(visit, attr) in [getattr(v, attr) for v in self.visits.values()]:
                raise AlreadyRegisteredVisit(
                    f"Visit already registered. Got visit={visit} "
                    f"(offending attr='{attr}'). "
                    f"See schedule '{self}'"
                )
        if not self.visits and visit.timepoint != self.base_timepoint:
            raise VisitTimepointError(
                f"First visit timepoint should be {self.base_timepoint}. Set schedule"
                f".base_timepoint if not using default base_timepoint of 0. "
                f"See {visit}. Got visit.timepoint={visit.timepoint}."
            )
        visit.base_timepoint = self.base_timepoint
        self.visits.update({visit.code: visit})
        return visit

    @property
    def field_value(self) -> str:
        return self.name

    def crf_required_at(self, label_lower: str) -> list[str]:
        """Returns a list of visit codes where the CRF is required
        by default.
        """
        visit_codes = []
        for visit_code, visit in self.visits.items():
            if label_lower in [form.model for form in visit.crfs if form.required]:
                visit_codes.append(visit_code)
        return visit_codes

    def requisition_required_at(self, requisition_panel) -> list[str]:
        """Returns a list of visit codes where the requisition is
        required by default.

        A requisition is found by its panel.
        """
        visit_codes = []
        for visit_code, visit in self.visits.items():
            if requisition_panel in [
                form.panel for form in visit.requisitions if form.required
            ]:
                visit_codes.append(visit_code)
        return visit_codes

    def subject(
        self, subject_identifier: str, consent_definition: ConsentDefinition = None
    ) -> SubjectSchedule:
        """Returns a SubjectSchedule instance for this subject.

        Note: SubjectSchedule puts a subject on/off schedule by
        updating the on/offschedule models
        """
        visit_schedule, schedule = site_visit_schedules.get_by_onschedule_model(
            self.onschedule_model
        )
        if schedule.name != self.name:
            raise ValueError(
                f"Site visit schedules return the wrong schedule object. "
                f"Expected {self!r} for onschedule_model={self.onschedule_model}. "
                f"Got {schedule!r}."
            )
        return SubjectSchedule(
            subject_identifier, visit_schedule=visit_schedule, schedule=self
        )

    def put_on_schedule(
        self,
        subject_identifier: str,
        onschedule_datetime: datetime | None,
        skip_baseline: bool | None = None,
        skip_get_current_site: bool | None = None,
        # consent_definition: ConsentDefinition = None,
    ) -> None:
        """Puts a subject onto this schedule.

        Wrapper of method SubjectSchedule.put_on_schedule.

        Appointment are created through this pathway.
        """
        rs = get_registered_subject_model_cls().objects.get(
            subject_identifier=subject_identifier
        )
        consent_definition = self.get_consent_definition(
            onschedule_datetime, site_sites.get(rs.site.id)
        )
        formatted_cdefs = [
            f"Cdef(proxy_model='{c.proxy_model}', version='{c.version}')"
            for c in self.consent_definitions
        ]
        if not consent_definition:
            raise ScheduleError(
                f"Consent definition may not be None. Expected one of {formatted_cdefs}."
            )

        if consent_definition not in self.consent_definitions:
            raise ScheduleError(
                "Invalid consent definition for schedule. Expected one of "
                f"{formatted_cdefs}. Got Cdef(proxy_model="
                f"'{consent_definition.proxy_model}', "
                f"version='{consent_definition.version}'). "
            )
        self.subject(
            subject_identifier, consent_definition=consent_definition
        ).put_on_schedule(
            onschedule_datetime,
            skip_baseline=skip_baseline,
            skip_get_current_site=skip_get_current_site,
            consent_definition=consent_definition,
        )

    def refresh_schedule(self, subject_identifier: str) -> None:
        self.subject(subject_identifier).refresh_appointments()

    def take_off_schedule(
        self, subject_identifier: str, offschedule_datetime: datetime
    ) -> None:
        """Wrapper of method SubjectSchedule.take_off_schedule."""
        self.subject(subject_identifier).take_off_schedule(offschedule_datetime)

    def is_onschedule(self, subject_identifier: str, report_datetime: datetime) -> bool:
        try:
            self.subject(subject_identifier).onschedule_or_raise(
                report_datetime=report_datetime, compare_as_datetimes=True
            )
        except (NotOnScheduleError, NotOnScheduleForDateError):
            return False
        return True

    def datetime_in_window(self, **kwargs):
        return self.window_cls(name=self.name, visits=self.visits, **kwargs).datetime_in_window

    @property
    def onschedule_model_cls(self) -> type[OnSchedule]:
        return django_apps.get_model(self.onschedule_model)

    @property
    def offschedule_model_cls(self) -> type[OffSchedule]:
        return django_apps.get_model(self.offschedule_model)

    @property
    def loss_to_followup_model_cls(self):
        return django_apps.get_model(self.loss_to_followup_model)

    @property
    def ltfu_model_cls(self):
        return self.loss_to_followup_model_cls

    @property
    def history_model_cls(self) -> type[SubjectScheduleHistory]:
        return django_apps.get_model(self.history_model)

    @property
    def appointment_model_cls(self) -> type[Appointment]:
        return django_apps.get_model(self.appointment_model)

    @property
    def visit_model_cls(self) -> type[RelatedVisitModel]:
        return self.appointment_model_cls.related_visit_model_cls()

    def get_consent_definition(
        self,
        report_datetime: datetime,
        site: SingleSite = None,
        consent_definition: ConsentDefinition = None,
    ) -> ConsentDefinition:
        """Returns the ConsentDefinition from this schedule valid for the
        given report date or raises an exception.
        """
        if consent_definition:
            consent_definitions = [
                c for c in self.consent_definitions if c.version == consent_definition.version
            ]
        else:
            consent_definitions = self.consent_definitions
        cdefs = [cdef for cdef in consent_definitions if site in cdef.sites]
        if not cdefs:
            cdefs_as_string = ", ".join(
                [cdef.display_name for cdef in self.consent_definitions]
            )
            raise ConsentDefinitionDoesNotExist(
                "This site does not match any consent definitions for this schedule. "
                f"Consent definitions are: {cdefs_as_string}. Got {site.name}."
            )

        cdefs = sorted(cdefs, key=lambda x: x.version, reverse=True)
        cdef = None
        for cdef in cdefs:
            try:
                cdef.valid_for_datetime_or_raise(report_datetime)
            except ConsentDefinitionValidityPeriodError:
                pass
            else:
                break
        if not cdef:
            date_string = formatted_date(report_datetime)
            cdefs_as_string = ", ".join(
                [cdef.display_name for cdef in self.consent_definitions]
            )
            raise ConsentDefinitionDoesNotExist(
                "Date does not fall within the validity period "
                "of any consent definition "
                f"for this schedule. Consent definitions are: "
                f"{cdefs_as_string}. Got {date_string}."
            )
        return cdef

    def to_dict(self):
        return {k: v.to_dict() for k, v in self.visits.items()}
