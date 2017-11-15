from django.apps import apps as django_apps
from django.core.exceptions import FieldError

from .constants import ALL_SITES


class EnrollmentCapError(Exception):
    pass


class EnrollmentCapReached(Exception):
    pass


class EnrollmentCap:

    def __init__(self, model=None, subject_type_name=None, study_site=None, max_subjects=None):
        self.model = model
        self.subject_type_name = subject_type_name
        self.study_site = study_site or ALL_SITES
        self.max_subjects = max_subjects
        self.name = f'{self.subject_type_name}.{self.model}.{self.study_site}'

    def __str__(self):
        return self.name

    @property
    def model_cls(self):
        try:
            model_cls = django_apps.get_model(self.model)
        except LookupError as e:
            raise EnrollmentCapError(e)
        return model_cls

    def fetch_count_or_raise(self):
        """Raises an exception if cap reached for this enrollment model
        and subject_type.
        """
        try:
            count = self.model_cls.objects.filter(
                subject_type=self.subject_type_name).count()
        except FieldError:
            count = self.model_cls.objects.all().count()
        if count >= self.max_subjects:
            raise EnrollmentCapReached(
                f'Enrollment cap reached for \'{self}\'.')
        return count
