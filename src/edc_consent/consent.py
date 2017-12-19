import arrow

from django.apps import apps as django_apps
from pprint import pprint


class ArrowObject:

    def __init__(self, start_dt, end_dt):
        self.rstart = arrow.Arrow.fromdatetime(
            start_dt, start_dt.tzinfo).to('utc')
        self.rend = arrow.Arrow.fromdatetime(end_dt, end_dt.tzinfo).to('utc')


class Consent:

    def __init__(self, model, **kwargs):
        """A class that represents the general attributes of a consent.
        """
        self.model_name = model
        self.group = kwargs.get('group', 'default')
        self.start = kwargs.get('start')
        self.start = arrow.Arrow.fromdatetime(
            self.start, self.start.tzinfo).to('UTC').datetime
        self.end = kwargs.get('end')
        self.end = arrow.Arrow.fromdatetime(
            self.end, self.end.tzinfo).to('UTC').datetime
        self.updates_versions = kwargs.get('updates_versions', [])
        self.version = kwargs.get('version', '0')
        self.gender = kwargs.get('gender', [])
        self.age_min = kwargs.get('age_min', 0)
        self.age_max = kwargs.get('age_max', 0)
        self.age_is_adult = kwargs.get('age_is_adult', 0)
        self.subject_type = kwargs.get('subject_type', 'subject')
        if self.updates_versions:
            if not isinstance(self.updates_versions, (list, tuple)):
                self.updates_versions = [
                    x.strip() for x in self.updates_versions.split(',')
                    if x.strip() != '']

    def __repr__(self):
        return (f'{self.__class__.__name__}({self.model_name}, {self.version})')

    def __str__(self):
        return self.name

    @property
    def name(self):
        return f'{self.model_name} {self.version}'

    @property
    def model(self):
        return django_apps.get_model(*self.model_name.split('.'))

    def for_datetime(self, dt):
        """Returns True of datetime is within start/end dates.
        """
        dt = arrow.get(dt, dt.tzinfo).to('UTC').datetime
        return self.start <= dt <= self.end

    def get_absolute_url(self):
        return self.model().get_absolute_url()

    @property
    def verbose_name(self):
        return self.model._meta.verbose_name

    @property
    def arrow(self):
        return ArrowObject(self.start, self.end)
