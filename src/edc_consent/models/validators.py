from django.core.exceptions import ValidationError


class SubjectTypeValidator:

    def __init__(self, model_cls):
        self.models_cls = model_cls

    def call(self, value):
        if value not in self.models_cls.SUBJECT_TYPES:
            raise ValidationError(
                'Undefined subject type. Expected one of {} for model {}. Got {}.'.format(
                    self.model_cls.SUBJECT_TYPES, self.model_cls._meta.verbose_name, value))
