import re

from django.core.management.color import color_style

from ..site_visit_schedules import site_visit_schedules, SiteVisitScheduleError
from ..subject_schedule import NotOnScheduleForDateError, NotOnScheduleError
from ..subject_schedule import SubjectSchedule, SubjectScheduleError
from ..visit import Visit
from .visit_collection import VisitCollection

style = color_style()


class ScheduleError(Exception):
    pass


class ScheduleNameError(Exception):
    pass


class AlreadyRegisteredVisit(Exception):
    pass


class Schedule:

    """A class that represents a "schedule" of visits.

    Is contained by a "visit schedule".

    Contains an ordered dictionary of visit instances and the onschedule
    and offschedule models used to get on and off the schedule.
    """

    name_regex = r"[a-z0-9\_\-]+$"
    visit_cls = Visit
    visit_collection_cls = VisitCollection
    subject_schedule_cls = SubjectSchedule

    def __init__(
        self,
        name=None,
        verbose_name=None,
        sequence=None,
        onschedule_model=None,
        offschedule_model=None,
        appointment_model=None,
        consent_model=None,
    ):
        self._subject = None
        self.visits = self.visit_collection_cls()
        if not name or not re.match(r"[a-z0-9\_\-]+$", name):
            raise ScheduleNameError(
                f"Invalid name. Got '{name}'. May only contains numbers, "
                "lower case letters and '_'."
            )
        else:
            self.name = name
        self.verbose_name = verbose_name or name
        self.sequence = sequence or name

        self.appointment_model = appointment_model.lower()
        self.consent_model = consent_model.lower()
        self.offschedule_model = offschedule_model.lower()
        self.onschedule_model = onschedule_model.lower()

    def check(self):
        warnings = []
        try:
            self.subject.check()
        except (SiteVisitScheduleError, SubjectScheduleError) as e:
            warnings.append(f"{e} See schedule '{self.name}'.")
        return warnings

    def __repr__(self):
        return f"Schedule({self.name})"

    def __str__(self):
        return self.name

    def add_visit(self, visit=None, **kwargs):
        """Adds a unique visit to the schedule.
        """
        visit = visit or self.visit_cls(**kwargs)
        for attr in ["code", "title", "timepoint", "rbase"]:
            if getattr(visit, attr) in [getattr(v, attr) for v in self.visits.values()]:
                raise AlreadyRegisteredVisit(
                    f"Visit already registered. Got visit={visit} ({attr}). "
                    f"See schedule '{self}'"
                )
        self.visits.update({visit.code: visit})
        return visit

    @property
    def field_value(self):
        return self.name

    @property
    def subject(self):
        """Returns a SubjectSchedule instance.

        Note: SubjectSchedule puts a subject on to a schedule or takes a subject
        off of a schedule.
        """
        if not self._subject:
            visit_schedule, schedule = site_visit_schedules.get_by_onschedule_model(
                self.onschedule_model
            )
            if schedule.name != self.name:
                raise ValueError(
                    f"Site visit schedules return the wrong schedule object. "
                    f"Expected {repr(self)} for onschedule_model={self.onschedule_model}. "
                    f"Got {repr(schedule)}."
                )
            self._subject = self.subject_schedule_cls(
                visit_schedule=visit_schedule, schedule=self
            )
        return self._subject

    def put_on_schedule(self, **kwargs):
        """Wrapper method to puts a subject onto this schedule.
        """
        self.subject.put_on_schedule(**kwargs)

    def refresh_schedule(self, **kwargs):
        """Resaves the onschedule model to, for example, refresh
        appointments.
        """
        self.subject.resave(**kwargs)

    def take_off_schedule(self, offschedule_datetime=None, **kwargs):
        self.subject.take_off_schedule(
            offschedule_datetime=offschedule_datetime, **kwargs
        )

    def is_onschedule(self, **kwargs):
        try:
            self.subject.onschedule_or_raise(compare_as_datetimes=True, **kwargs)
        except (NotOnScheduleError, NotOnScheduleForDateError):
            return False
        return True

    @property
    def onschedule_model_cls(self):
        return self.subject.onschedule_model_cls

    @property
    def offschedule_model_cls(self):
        return self.subject.offschedule_model_cls

    @property
    def history_model_cls(self):
        return self.subject.history_model_cls

    @property
    def appointment_model_cls(self):
        return self.subject.appointment_model_cls

    @property
    def visit_model_cls(self):
        return self.subject.visit_model_cls

    @property
    def consent_model_cls(self):
        return self.subject.consent_model_cls

    def to_dict(self):
        return {k: v.to_dict() for k, v in self.visits.items()}
