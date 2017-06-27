from django.apps import apps as django_apps
from edc_protocol.exceptions import SubjectTypeCapError

ALL_SITES = 'ALL'


class Cap:

    def __init__(self, subject_type_name=None, model_name=None,
                 study_site=None, max_subjects=None):
        self.subject_type_name = subject_type_name
        self.model_name = model_name
        self.study_site = study_site or ALL_SITES
        max_subjects = max_subjects or 0
        if max_subjects <= 0:
            raise SubjectTypeCapError(
                'Subject type cap must be greater than 0. Got max_subjects={}. '
                'See edc_protocol.app_config'.format(max_subjects))
        self.max_subjects = max_subjects or -1

    def __repr__(self):
        return (f'{self.__class__.__name__}(study_site={self.study_site}, '
                f'max={self.max_subjects})')

    def __str__(self):
        return (f'{self.subject_type_name} model={self.model_name}, '
                f'study_sites={self.study_site}, max={self.max_subjects}')

    @property
    def name(self):
        return f'{self.subject_type_name}:{self.model_name}:{self.study_site}'

    @property
    def model(self):
        return django_apps.get_model(*self._model)
