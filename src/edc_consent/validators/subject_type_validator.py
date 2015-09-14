from django.core.exceptions import ValidationError


class SubjectTypeValidator:

    def __init__(self, subject_types):
        self.subject_types = subject_types

    def call(self, value):
        if value not in self.subject_types:
            raise ValidationError(
                'Undefined subject type. Expected one of {} for model {}. Got {}.'.format(
                    self.subject_types, self.model_cls._meta.verbose_name, value))
