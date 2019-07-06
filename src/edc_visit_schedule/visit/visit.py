import re

from decimal import Decimal
from django.apps import apps as django_apps

from .window_period import WindowPeriod


class VisitCodeError(Exception):
    pass


class VisitDateError(Exception):
    pass


class VisitError(Exception):
    pass


class VisitDate:

    window_period_cls = WindowPeriod

    def __init__(self, **kwargs):
        self._base = None
        self._window = self.window_period_cls(**kwargs)
        self.lower = None
        self.upper = None

    @property
    def base(self):
        return self._base

    @base.setter
    def base(self, dt=None):
        self._base = dt
        window = self._window.get_window(dt=dt)
        self.lower = window.lower
        self.upper = window.upper


class Visit:

    code_regex = r"^([A-Z0-9])+$"
    visit_date_cls = VisitDate

    def __init__(
        self,
        code=None,
        timepoint=None,
        rbase=None,
        rlower=None,
        rupper=None,
        crfs=None,
        requisitions=None,
        crfs_unscheduled=None,
        requisitions_unscheduled=None,
        crfs_prn=None,
        requisitions_prn=None,
        title=None,
        instructions=None,
        grouping=None,
        allow_unscheduled=None,
        facility_name=None,
    ):

        self.crfs = ()
        if crfs:
            self.crfs = crfs.forms
        self.crfs_unscheduled = ()
        if crfs_unscheduled:
            self.crfs_unscheduled = crfs_unscheduled.forms
        self.crfs_prn = ()
        if crfs_prn:
            self.crfs_prn = crfs_prn.forms
        self.requisitions = ()
        if requisitions:
            self.requisitions = requisitions.forms
        self.requisitions_unscheduled = ()
        if requisitions_unscheduled:
            self.requisitions_unscheduled = requisitions_unscheduled.forms
        self.requisitions_prn = ()
        if requisitions_prn:
            self.requisitions_prn = requisitions_prn.forms
        self.instructions = instructions
        self.timepoint = Decimal(str(timepoint))
        self.rbase = rbase
        self.rlower = rlower
        self.rupper = rupper
        self.grouping = grouping
        self.dates = self.visit_date_cls(rlower=rlower, rupper=rupper)
        self.title = title or f"Visit {code}"
        if not code or isinstance(code, int) or not re.match(self.code_regex, code):
            raise VisitCodeError(f"Invalid visit code. Got '{code}'")
        else:
            self.code = code  # unique
        self.name = self.code
        self.facility_name = facility_name
        self.allow_unscheduled = allow_unscheduled
        if timepoint is None:
            raise VisitError(f"Timepoint not specified. Got None. See Visit {code}.")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.code}, {self.timepoint})"

    def __str__(self):
        return self.title

    @property
    def forms(self):
        """Returns a list of scheduled forms.
        """
        return self.crfs + self.requisitions

    @property
    def unscheduled_forms(self):
        """Returns a list of unscheduled forms.
        """
        return self.crfs_unscheduled + self.requisitions_unscheduled

    @property
    def prn_forms(self):
        """Returns a list of PRN forms.
        """
        return self.crfs_prn + self.requisitions_prn

    @property
    def all_crfs(self):
        return self.crfs + self.crfs_unscheduled + self.crfs_prn

    @property
    def all_requisitions(self):
        names = list(set([r.name for r in self.requisitions]))
        requisitions = list(self.requisitions) + [
            r for r in self.requisitions_unscheduled if r.name not in names
        ]
        names = list(set([r.name for r in requisitions]))
        requisitions = requisitions + [
            r for r in self.requisitions_prn if r.name not in names
        ]
        return sorted(requisitions, key=lambda x: x.show_order)

    def next_form(self, model=None, panel=None):
        """Returns the next required "form" or None.
        """
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
    def facility(self):
        """Returns a Facility object.
        """
        if self.facility_name:
            app_config = django_apps.get_app_config("edc_facility")
            return app_config.get_facility(name=self.facility_name)
        return None

    @property
    def timepoint_datetime(self):
        return self.dates.base

    @timepoint_datetime.setter
    def timepoint_datetime(self, dt=None):
        self.dates.base = dt

    def check(self):
        warnings = []
        try:
            for crf in self.crfs:
                django_apps.get_model(crf.model)
            for crf in self.requisitions:
                django_apps.get_model(crf.model)
            for crf in self.crfs_unscheduled:
                django_apps.get_model(crf.model)
            for crf in self.requisitions_unscheduled:
                django_apps.get_model(crf.model)
        except LookupError as e:
            warnings.append(f"{e} Got Visit {self.code} crf.model={crf.model}.")
        return warnings

    def to_dict(self):
        return dict(
            crfs=[(crf.model, crf.required) for crf in self.crfs],
            crfs_unscheduled=[
                (crf.model, crf.required) for crf in self.crfs_unscheduled
            ],
            requisitions=[
                (requisition.panel.name, requisition.required)
                for requisition in self.requisitions
            ],
            requisitions_unscheduled=[
                (requisition.panel.name, requisition.required)
                for requisition in self.requisitions_unscheduled
            ],
        )
