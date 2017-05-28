import re

from .get_model import get_model


class ValidatorLookupError(Exception):
    pass


class ValidatorModelFieldError(Exception):
    pass


class ValidatorMetaAttributeError(Exception):
    pass


class ValidatorMetaFormatError(Exception):
    pass


class ValidatorMetaValueError(Exception):
    pass


class Validator:

    """A class that validates models used by VisitSchedule and Schedule.

    Keyword args:
        * `model`: label lower of model (Required).
        * `required_fields`: a list of field names that must exist on the model.
        * `visit_schedule_name`: part0 of _meta.visit_schedule_name (part0.part1)
        * `schedule_name`: part1 of _meta.visit_schedule_name (part0.part1)

    if either `visit_schedule_name` or `schedule_name` are specified, model class
        _meta attribute is validated.
    """

    func_get_model = get_model
    meta_pattern = r'(^([a-z0-9]+[\_]{0,1})+([a-z0-9]+){1}\.([a-z0-9]+[\_]{0,1})+[a-z0-9]+$)'

    def __init__(self, visit_schedule_name=None, schedule_name=None, model=None,
                 required_fields=None, meta_pattern=None, **kwargs):
        self._model_cls = None
        self.meta_pattern = re.compile(meta_pattern or self.meta_pattern)
        self.model_label_lower = model
        self.required_fields = required_fields or []
        self.name = visit_schedule_name or schedule_name
        if not self.name:
            self.name = model
            self.require_meta = False
        else:
            self.require_meta = True
            if visit_schedule_name:
                self.INDEX = 0
            elif schedule_name:
                self.INDEX = 1

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name}, {self.model_label_lower})'

    def __str__(self):
        return f'{self.name} {self.model_label_lower}'

    @property
    def validated_model(self):
        if self.require_meta:
            self.validate_meta_or_raise()
        if self.required_fields:
            self.validate_fields_or_raise()
        return self._model

    @property
    def _model(self):
        """Returns an unvalidated model class or raises.
        """
        if not self._model_cls:
            try:
                self._model_cls = self.func_get_model(
                    model=self.model_label_lower)
            except LookupError as e:
                raise ValidatorLookupError(e) from e
        return self._model_cls

    def validate_meta_or_raise(self):
        """Validates _meta.visit_schedule_name as valid or raises.

        Checks if _meta attr exists, matches the meta_pattern, and corresponds
        with the given part "self.name".
        """
        try:
            self._model._meta.visit_schedule_name
        except AttributeError:
            raise ValidatorMetaAttributeError(
                f'Model \'{self._model._meta.label_lower}\' is missing _meta attribute '
                f'\'visit_schedule_name\'. See \'{self.__repr__()}\'')
        else:
            if not re.match(self.meta_pattern, self._model._meta.visit_schedule_name):
                raise ValidatorMetaFormatError(
                    f'Model \'{self._model._meta.label_lower}\' _meta.visit_schedule_name '
                    f'value has an invalid format. Got \'{self._model._meta.visit_schedule_name}\'. '
                    f'See \'{self.__repr__()}\'')
            name = self._model._meta.visit_schedule_name.split('.')[
                self.INDEX]
            try:
                assert name == self.name
            except AssertionError as e:
                raise ValidatorMetaValueError(
                    f'Expected \'{self.name}\'. Got \'{name}\' from the model. '
                    f'See Model \'{self._model._meta.label_lower}._meta.visit_schedule_name\'.'
                ) from e

    def validate_fields_or_raise(self):
        """Validates required fields exist on the model or raises.
        """
        if not [f.name for f in self._model._meta.fields if f.name in self.required_fields]:
            fields = ', '.join(self.required_fields)
            raise ValidatorModelFieldError(
                f'Model \'{self._model._meta.label_lower}\' is missing one or more required fields. '
                f'Expected \'{fields}\'.')
