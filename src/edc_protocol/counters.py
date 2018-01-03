from django.apps import apps as django_apps
from django.core.exceptions import FieldError


class CounterError(Exception):
    pass


class MaximumReached(Exception):
    pass


class Counter:

    model = 'edc_identifier.identifiermodel'

    def __init__(self, subject_type=None, site_id=None, max_count=None,
                 subject_type_plural=None):
        self._site = None
        self.subject_type = subject_type
        self.site_id = site_id
        self.max_count = max_count
        subject_type_plural = subject_type_plural or f'{self.subject_type}s'
        self.message = f'Maximum {subject_type_plural} reached'
        self.query_options = dict(subject_type=self.subject_type)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.site_id})'

    def __str__(self):
        return f'site:{self.site} max:{self.max_subjects}'

    @property
    def site(self):
        if not self._site:
            if self.site_id:
                from django.contrib.sites.models import Site
                self._site = Site.objects.get(pk=self.site_id)
        return self._site

    @property
    def model_cls(self):
        return django_apps.get_model(self.model)

    def get_count_or_raise(self, site=None):
        if self.site and site != self.site:
            raise CounterError(
                f'Invalid site for counter. Expected {self.site}. '
                f'Got {site}. See {repr(self)}.')
        if self.site:
            self.query_options.update(site=self.site)
        count = self.model_cls.objects.filter(**self.query_options).count()
        if count >= self.max_subjects:
            if self.site:
                message = f'{self.message} for site {self.site.name}'
            raise MaximumReached(f'{message}.')


class SubjectIdentifierCounter(Counter):

    pass


class SubjectModelCounter(Counter):

    def __init__(self, model=None, site_id=None, max_count=None):
        super().__init__(site_id=site_id, max_count=max_count)
        self.model = model
        self.query_options = {}
        self.message = f'Maximum reached for {self.model}'
