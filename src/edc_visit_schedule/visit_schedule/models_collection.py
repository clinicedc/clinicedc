from collections import OrderedDict

from ..validator import Validator, ValidatorLookupError


class ModelsCollectionError(Exception):
    pass


class ModelsCollection(OrderedDict):

    model_validator_cls = Validator
    onschedule_model_required_fields = [
        'onschedule_datetime', 'visit_schedule_name', 'schedule_name']

    onschedule_model = None
    offschedule_model = None

    def __init__(self, visit_schedule_name=None, *args, **kwargs):
        self.visit_schedule_name = visit_schedule_name
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'{self.__class__.__name__}(name=\'{self.visit_schedule_name}\')'

    def update(self, **kwargs):
        """Updates the dict with key/value pair where
        value is a model's label_lower.
        """
        for key, value in kwargs.items():
            if value:
                value = value.lower()
            setattr(self, key, value)
            super().update({key: value})

    def validate(self):
        """Raises an exception if a model cannot be validated.
        """
        for key, model in self.items():
            if model:
                if key in ['onschedule_model', 'offschedule_model']:
                    validator = self.model_validator_cls(
                        model=model,
                        visit_schedule_name=self.visit_schedule_name,
                        required_fields=self.onschedule_model_required_fields)
                else:
                    validator = self.model_validator_cls(model=model)
                try:
                    validator.validated_model
                except ValidatorLookupError as e:
                    raise ModelsCollectionError(
                        f'{e}. Got {key}={model}. Visit schedule='
                        f'{self.visit_schedule_name}.')
