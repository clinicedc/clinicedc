import re

from dateutil.relativedelta import relativedelta

from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist

from .exceptions import AlreadyRegistered, ScheduleError, CrfError
from .visit import Visit


class Schedule:
    def __init__(self, name, enrollment_model=None, disenrollment_model=None):
        self.death_report_model = None
        self.disenrollment_model = None
        self.enrollment_model = None
        self.offstudy_model = None
        self.visit_model = None
        self.visit_registry = {}
        self.name = name
        if not re.match(r'[a-z0-9\_\-]+$', name):
            raise ImproperlyConfigured('Schedule name may only contains numbers, lower case letters and \'_\'.')
        if disenrollment_model:
            self.disenrollment_model = django_apps.get_model(*disenrollment_model.split('.'))
        if enrollment_model:
            self.enrollment_model = django_apps.get_model(*enrollment_model.split('.'))

    def __repr__(self):
        return '<Schedule({}, {})>'.format(self.name, self.enrollment_model._meta.label_lower)

    def __str__(self):
        return self.name

    def enrollment_instance(self, subject_identifier):
        """Returns the enrollment model instance or None."""
        try:
            enrollment_instance = self.enrollment_model.objects.get(subject_identifier=subject_identifier)
        except ObjectDoesNotExist:
            enrollment_instance = None
        return enrollment_instance

    def add_visit(self, code, **kwargs):
        visit = Visit(code, **kwargs)
        if visit.code in self.visit_registry:
            raise AlreadyRegistered(
                'Visit is already registered with schedule \'{}\'. Got {}'.format(self.name, visit))
        if visit.timepoint in [v.timepoint for v in self.visit_registry.values()]:
            raise ScheduleError(
                'Visit with timepoint \'{}\' already registered with schedule \'{}\'. Got {}'.format(
                    visit.timepoint, self.name, visit))
        if visit.base_interval in [v.base_interval for v in self.visit_registry.values()]:
            raise ScheduleError(
                'Visit with base_interval \'{}\' already registered with schedule \'{}\'. Got {}'.format(
                    visit.base_interval, self.name, visit))
        if kwargs.get('crfs'):
            show_orders = sorted([crf.show_order for crf in kwargs.get('crfs')])
            if len(list(set(show_orders))) != len(show_orders):
                raise CrfError(
                    'Crf show order must be a unique sequence. Got {} in schedule {}'.format(show_orders, self.name))
        self.visit_registry.update({code: visit})
        return visit

    def get_visit(self, code, interval=None):
        visit = self.visit_registry.get(code)
        if interval:
            if interval > 0:
                visits = [v for v in self.visits if v.timepoint > visit.timepoint]
            else:
                visits = [i for i in reversed([v for v in self.visits if v.timepoint < visit.timepoint])]
            try:
                visit = visits[abs(interval) - 1]
            except IndexError:
                visit = None
        return visit

    def get_first_visit(self):
        """Returns the previous visit or None."""
        return self.visits[0]

    def get_previous_visit(self, code):
        """Returns the previous visit or None."""
        return self.get_visit(code, -1)

    def get_next_visit(self, code):
        """Returns the previous visit or None."""
        return self.get_visit(code, 1)

    @property
    def visits(self):
        ordered_visits = sorted(self.visit_registry.values(), key=lambda x: x.timepoint)
        return [x for x in ordered_visits]

    def relativedelta_from_base(self, code=None):
        """Returns the relativedelta from the zero timepoint visit."""
        visit = self.visit_registry.get(code)
        if visit.base_interval == 0:
            rdelta = relativedelta(days=0)
        else:
            rdelta = relativedelta(**{visit.base_interval_unit: visit.base_interval})
        return rdelta
