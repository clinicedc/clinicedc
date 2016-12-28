import arrow

from django.apps import apps as django_apps


class Consent:

    def __init__(self, model, **kwargs):
        """A class that represents the general attributes of a consent."""
        self.model_name = model
        self.end = kwargs.get('end')
        self.end = arrow.get(self.end, self.end.tzinfo).to('UTC').datetime
        self.start = kwargs.get('start')
        self.start = arrow.get(self.start, self.start.tzinfo).to('UTC').datetime
        self.updates_versions = kwargs.get('updates_versions', [])
        self.version = kwargs.get('version', '0')
        self.gender = kwargs.get('gender', [])
        self.age_min = kwargs.get('age_min', 0)
        self.age_max = kwargs.get('age_max', 0)
        self.age_is_adult = kwargs.get('age_is_adult', 0)
        self.subject_type = kwargs.get('subject_type', 'subject')
        if self.updates_versions:
            if not isinstance(self.updates_versions, (list, tuple)):
                self.updates_versions = [x.strip() for x in self.updates_versions.split(',') if x.strip() != '']

    def __repr__(self):
        return '{0}(consent_model={1.model_name}, version={1.version}, ...)'.format(
            self.__class__.__name__, self)

    def __str__(self):
        return self.name

    @property
    def name(self):
        return '{}-{}'.format(self.model_name, self.version)

    @property
    def model(self):
        return django_apps.get_model(*self.model_name.split('.'))

    def for_datetime(self, dt):
        """Returns True of datetime is within start/end dates."""
        dt = arrow.get(dt, dt.tzinfo).to('UTC').datetime
        return self.start <= dt <= self.end
