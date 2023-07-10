from __future__ import annotations

import re
from decimal import Decimal
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from edc_facility.utils import get_default_facility_name, get_facility
from edc_utils import get_utcnow, to_utc

from .window_period import WindowPeriod

if TYPE_CHECKING:
    from datetime import datetime

    from dateutil.relativedelta import relativedelta
    from edc_facility import Facility

    from .forms_collection import FormsCollection


class VisitCodeError(Exception):
    pass


class VisitDateError(Exception):
    pass


class VisitError(Exception):
    pass


class BaseDatetimeNotSet(Exception):
    pass


def base_datetime_required():
    raise BaseDatetimeNotSet(
        "Base datetime is None, set the base datetime before accessing attr"
    )


class VisitDate:
    window_period_cls = WindowPeriod

    def __init__(
        self,
        rlower: relativedelta = None,
        rupper: relativedelta = None,
        timepoint: Decimal = None,
        base_timepoint: Decimal = None,
    ):
        self._base: datetime | None = None
        self._lower: datetime | None = None
        self._upper: datetime | None = None
        self._window_period = self.window_period_cls(
            rlower=rlower,
            rupper=rupper,
            timepoint=timepoint,
            base_timepoint=base_timepoint,
        )

    @property
    def base(self) -> datetime:
        return self._base

    @base.setter
    def base(self, dt: datetime = None):
        self._base = to_utc(dt)
        self._lower, self._upper = self._window_period.get_window(dt=self._base)

    @property
    def lower(self) -> datetime:
        if not self.base:
            raise BaseDatetimeNotSet(
                "Base datetime is None, set the base datetime before accessing attr lower"
            )
        return self._lower

    @property
    def upper(self) -> datetime:
        if not self.base:
            raise BaseDatetimeNotSet(
                "Base datetime is None, set the base datetime before accessing attr upper"
            )
        return self._upper


class Visit:
    code_regex = r"^([A-Z0-9])+$"
    visit_date_cls = VisitDate

    def __init__(
        self,
        code: str = None,
        timepoint: int | float | Decimal = None,
        rbase: relativedelta = None,
        rlower: relativedelta = None,
        rupper: relativedelta = None,
        rlower_late: relativedelta = None,
        rupper_late: relativedelta = None,
        add_window_gap_to_lower: bool | None = None,
        max_window_gap_to_lower: int | None = None,
        crfs: FormsCollection | None = None,
        requisitions: FormsCollection | None = None,
        crfs_unscheduled: FormsCollection | None = None,
        crfs_missed: FormsCollection | None = None,
        requisitions_unscheduled: FormsCollection | None = None,
        crfs_prn: FormsCollection | None = None,
        requisitions_prn: FormsCollection | None = None,
        title: str = None,
        allow_unscheduled: bool | None = None,
        facility_name: str | None = None,
        instructions: str | None = None,
        base_timepoint: int | float | Decimal | None = None,
        grouping=None,
    ):
        self.next = None
        if isinstance(base_timepoint, (float,)):
            base_timepoint = Decimal(str(base_timepoint))
        elif isinstance(base_timepoint, (int,)):
            base_timepoint = Decimal(str(base_timepoint) + ".0")
        self.base_timepoint = base_timepoint or Decimal("0.0")
        self.crfs = crfs.forms if crfs else tuple()
        self.crfs_unscheduled = crfs_unscheduled.forms if crfs_unscheduled else ()
        self.crfs_missed = crfs_missed.forms if crfs_missed else ()
        self.crfs_prn = crfs_prn.forms if crfs_prn else ()
        for prn in self.crfs_prn:
            prn.required = False
        self.requisitions = requisitions.forms if requisitions else ()
        self.requisitions_unscheduled = (
            requisitions_unscheduled.forms if requisitions_unscheduled else ()
        )
        self.requisitions_prn = requisitions_prn.forms if requisitions_prn else ()
        for prn in self.requisitions_prn:
            prn.required = False
        self.instructions = instructions
        if isinstance(timepoint, (float,)):
            timepoint = Decimal(str(timepoint))
        elif isinstance(timepoint, (int,)):
            timepoint = Decimal(str(timepoint) + ".0")
        self.timepoint = timepoint
        self.rbase = rbase
        self.rlower = rlower
        self.rupper = rupper
        self.rlower_late = self.rlower if rlower_late is None else rlower_late
        self.rupper_late = self.rupper if rupper_late is None else rupper_late
        self.add_window_gap_to_lower = add_window_gap_to_lower
        self.max_window_gap_to_lower = max_window_gap_to_lower
        self.grouping = grouping
        if not code or isinstance(code, int) or not re.match(self.code_regex, code):
            raise VisitCodeError(f"Invalid visit code. Got '{code}'")
        else:
            self.code = code  # unique
        self.dates = self.visit_date_cls(
            rlower=rlower,
            rupper=rupper,
            timepoint=self.timepoint,
            base_timepoint=self.base_timepoint,
        )
        self.late_dates = self.visit_date_cls(
            rlower=rlower_late or rlower,
            rupper=rupper_late or rupper,
            timepoint=self.timepoint,
            base_timepoint=self.base_timepoint,
        )
        utcnow = get_utcnow()
        self.validate_rlower_late(utcnow)
        self.validate_rupper_late(utcnow)
        self.title = title or f"Visit {self.code}"
        self.name = self.code
        self.facility_name = facility_name or get_default_facility_name()
        self.allow_unscheduled = allow_unscheduled
        if timepoint is None:
            raise VisitError(f"Timepoint not specified. Got None. See Visit {code}.")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.code}, {self.timepoint})"

    def __str__(self):
        return self.title

    @property
    def forms(self):
        """Returns a list of scheduled forms."""
        return self.crfs + self.requisitions

    @property
    def unscheduled_forms(self):
        """Returns a list of unscheduled forms."""
        return self.crfs_unscheduled + self.requisitions_unscheduled

    @property
    def missed_forms(self):
        """Returns a list of forms to show for a missed visit."""
        return self.crfs_missed

    @property
    def prn_forms(self):
        """Returns a list of PRN forms."""
        return self.crfs_prn + self.requisitions_prn

    @property
    def all_crfs(self):
        return self.crfs + self.crfs_unscheduled + self.crfs_prn + self.crfs_missed

    @property
    def all_requisitions(self):
        names = list(set([r.name for r in self.requisitions]))
        requisitions = list(self.requisitions) + [
            r for r in self.requisitions_unscheduled if r.name not in names
        ]
        names = list(set([r.name for r in requisitions]))
        requisitions = requisitions + [r for r in self.requisitions_prn if r.name not in names]
        return sorted(requisitions, key=lambda x: x.show_order)

    def next_form(self, model=None, panel=None):
        """Returns the next required "form" or None."""
        next_form = None
        for index, form in enumerate(self.forms):
            if form.model == model and form.required:
                try:
                    next_form = self.forms[index + 1]
                except IndexError:
                    pass
        return next_form

    def get_form(self, model=None):
        for form in self.forms:
            if form.model == model:
                return form
        return None

    def get_crf(self, model=None):
        get_crf = None
        for crf in self.crfs:
            if crf.model == model:
                get_crf = crf
                break
        return get_crf

    def get_requisition(self, model=None, panel_name=None):
        get_requisition = None
        for requisition in self.requisitions:
            if requisition.model == model and requisition.panel.name == panel_name:
                get_requisition = requisition
                break
        return get_requisition

    @property
    def facility(self) -> Facility | None:
        """Returns a Facility object."""
        if self.facility_name:
            return get_facility(name=self.facility_name)
        return None

    @property
    def timepoint_datetime(self) -> datetime:
        return self.dates.base

    @timepoint_datetime.setter
    def timepoint_datetime(self, dt=None):
        self.dates.base = to_utc(dt)

    def check(self):
        warnings = []
        crf = None
        try:
            for crf in self.crfs:
                django_apps.get_model(crf.model)
            for crf in self.requisitions:
                django_apps.get_model(crf.model)
            for crf in self.crfs_unscheduled:
                django_apps.get_model(crf.model)
            for crf in self.crfs_missed:
                django_apps.get_model(crf.model)
            for crf in self.requisitions_unscheduled:
                django_apps.get_model(crf.model)
        except LookupError as e:
            warnings.append(f"{e} Got Visit {self.code} crf.model={crf.model}.")
        return warnings

    def to_dict(self):
        return dict(
            crfs=[(crf.model, crf.required) for crf in self.crfs],
            crfs_unscheduled=[(crf.model, crf.required) for crf in self.crfs_unscheduled],
            requisitions=[
                (requisition.panel.name, requisition.required)
                for requisition in self.requisitions
            ],
            requisitions_unscheduled=[
                (requisition.panel.name, requisition.required)
                for requisition in self.requisitions_unscheduled
            ],
        )

    def validate_rlower_late(self, utcnow):
        if utcnow - self.rlower_late < utcnow - self.rlower:
            raise VisitDateError(
                "Lower bound error. `Late` lower boundary cannot exceed "
                f"lower boundary. See {self}."
            )

    def validate_rupper_late(self, utcnow):
        if utcnow + self.rupper_late < utcnow + self.rupper:
            raise VisitDateError(
                "Upper bound error. `Late` upper boundary cannot be exceed "
                f"upper boundary. See {self}."
            )
