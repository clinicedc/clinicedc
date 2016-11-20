import re

from dateutil.relativedelta import relativedelta

from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured

from .exceptions import AlreadyRegistered, ScheduleError, CrfError
from .visit import Visit


class Schedule:
    def __init__(self, name):
        self.name = name
        if not re.match(r'[a-z0-9\_\-]+$', name):
            raise ImproperlyConfigured('Schedule name may only contains numbers, lower case letters and \'_\'.')
        self.death_report_model = None
        self.disenrollment_model = None
        self.enrollment_model = None
        self.offstudy_model = None
        self.visit_model = None
        self.visit_registry = {}

    def __repr__(self):
        return '<Schedule({}, {})>'.format(self.name, self.enrollment_model._meta.label_lower)

    def __str__(self):
        return self.name

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

    def add_enrollment_model(self, model):
        self.enrollment_model = django_apps.get_model(*model.split('.'))
        try:
            self.enrollment_model.create_appointments
        except AttributeError as e:
            raise ImproperlyConfigured(
                'Schedule enrollment model cannot be an \'schedule enrollment model\'. It is not configured '
                'to create appointments. Got {}'.format(str(e)))
        self.validate_modelmixin_attrs(self.enrollment_model)

    def add_disenrollment_model(self, model):
        self.disenrollment_model = django_apps.get_model(*model.split('.'))
        self.validate_modelmixin_attrs(self.disenrollment_model)

    def add_death_report_model(self, model):
        self.death_report_model = django_apps.get_model(*model.split('.'))

    def add_offstudy_model(self, model):
        self.offstudy_model = django_apps.get_model(*model.split('.'))

    def add_visit_model(self, model):
        self.visit_model = django_apps.get_model(*model.split('.'))

    def validate_modelmixin_attrs(self, model):
        """Validate that the attrs from the enrollment/disenrollment model_mixins exist."""
        try:
            getattr(getattr(model, '_meta'), 'visit_schedule_name')
        except AttributeError as e:
                raise ImproperlyConfigured(
                    'The {} for schedule \'{}\' is missing \'_meta\' attribute \'visit_schedule_name\'. Got {}'.format(
                        ' '.join(model._meta.label_lower.split('.')), self.name, str(e)))
        for field in ['report_datetime', 'schedule_name']:
            try:
                getattr(model, field)
            except AttributeError as e:
                raise ImproperlyConfigured(
                    'The {} for schedule \'{}\' is missing field \'{}\'. Got {}'.format(
                        ' '.join(model._meta.label_lower.split('.')), self.name, field, str(e)))
