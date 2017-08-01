from django.apps import apps as django_apps
from django.core.exceptions import FieldError

from .cap import ALL_SITES


class EnrollmentCapError(Exception):
    pass


class EnrollmentCapReached(Exception):
    pass


class EnrollmentCap:

    def __init__(self, model=None, subject_type_name=None, study_site=None):
        try:
            self.model = django_apps.get_model(*model.split('.'))
        except ValueError:
            self.model = model
        except LookupError as e:
            raise EnrollmentCapError(e)
        self.subject_type_name = subject_type_name
        self.study_site = study_site or ALL_SITES
        app_config = django_apps.get_app_config('edc_protocol')
        self.cap = app_config.subject_types.get(
            f'{self.subject_type_name}:{model}:{study_site}')
        if not self.cap:
            key = f'{self.subject_type_name}:{model}:{ALL_SITES}'
            self.cap = app_config.subject_types.get(key)
            if not self.cap:
                raise EnrollmentCapError(
                    f'Unknown enrollment cap. Got \'{key}\'. '
                    f'Expected one of {list(app_config.subject_types.keys())}. '
                    'See edc_protocol.')

    def fetch_or_raise_on_cap_met(self):
        """Raises an exception if cap reached for this enrollment model
        and subject_type.
        """
        try:
            count = self.model.objects.filter(
                subject_type=self.cap.subject_type_name).count()
        except FieldError:
            count = self.model.objects.all().count()
        if count >= self.cap.max_subjects:
            raise EnrollmentCapReached(
                f'Enrollment cap reached for \'{self.cap}\'.')
        return count, self.cap.max_subjects
