from django.apps import apps as django_apps


class ModelValidatorError(Exception):
    pass


class EnrollmentModelValidatorError(Exception):
    pass


class DisenrollmentModelValidatorError(Exception):
    pass


def get_model(model=None, required=None):
    """Returns the model class or None.
    """
    try:
        model._meta.label_lower
    except AttributeError as e:
        try:
            model = django_apps.get_model(*model.split('.'))
        except (LookupError, AttributeError, ValueError) as e:
            if required or model:
                raise LookupError(f'Model=\'{model}\'. Got {e}.') from e
            else:
                pass
    return model


class BaseModelValidator:

    exception_cls = ModelValidatorError

    def __init__(self, model=None, required=None, **kwargs):
        try:
            self.model = get_model(model=model, required=required)
        except LookupError as e:
            raise self.exception_cls(e) from e
        self.validate()

    def validate(self):
        pass


class BaseEnrollmentModelValidator(BaseModelValidator):

    exception_cls = None

    def __init__(self, visit_schedule_name=None, **kwargs):
        self.visit_schedule_name = visit_schedule_name
        super().__init__(**kwargs)

    def validate(self):
        super().validate()
        try:
            self.model._meta.visit_schedule_name
        except AttributeError:
            raise self.exception_cls(
                f'Model \'{self.model._meta.label_lower}\' is missing _meta attribute '
                f'\'visit_schedule_name\'. See visit schedule \'{self.visit_schedule_name}\'')
        else:
            try:
                assert self.model._meta.visit_schedule_name.split(
                    '.')[0] == self.visit_schedule_name
            except AttributeError as e:
                raise self.exception_cls(
                    f'Invalid visit_schedule_name. '
                    f'Got {self.model._meta.visit_schedule_name}. '
                    f'See model \'{self.model._meta.label_lower}\'.') from e
            except AssertionError as e:
                raise self.exception_cls(
                    f'Expected \'{self.visit_schedule_name}\'. Got \'{self.model._meta.visit_schedule_name}\'. '
                    f'See Model \'{self.model._meta.label_lower}._meta.visit_schedule_name\'') from e
            if not [f.name for f in self.model._meta.fields if f.name in [
                    'report_datetime', 'schedule_name']]:
                raise self.exception_cls(
                    f'Model \'{self.model._meta.label_lower}\' is missing one or more required fields. '
                    f'Expected \'report_datetime\' and \'schedule_name\'.')
        return self.model


class EnrollmentModelValidator(BaseEnrollmentModelValidator):

    exception_cls = EnrollmentModelValidatorError

    def validate(self):
        super().validate()
        try:
            self.model.create_appointments
        except AttributeError as e:
            raise self.exception_cls(
                f'{self.model._meta.verbose_name} is not '
                f'configured to create appointments. Got {e}') from e
        return self.model


class DisenrollmentModelValidator(BaseEnrollmentModelValidator):

    exception_cls = DisenrollmentModelValidatorError


class ModelValidator:

    disenrollment_model_validator = DisenrollmentModelValidator
    enrollment_model_validator = EnrollmentModelValidator
    model_validator = BaseModelValidator

    def __init__(self, visit_schedule_name=None, enrollment_model=None,
                 disenrollment_model=None, visit_model=None,
                 offstudy_model=None, death_report_model=None):

        try:
            self.death_report_model = self.model_validator(
                model=death_report_model, required=True,
                visit_schedule_name=visit_schedule_name).model
        except ModelValidatorError as e:
            raise ModelValidatorError(
                f'death report model: {e}. See {visit_schedule_name}') from e

        try:
            self.visit_model = self.model_validator(
                model=visit_model, required=True,
                visit_schedule_name=visit_schedule_name).model
        except ModelValidatorError as e:
            raise ModelValidatorError(
                f'visit model: {e}. See {visit_schedule_name}') from e

        try:
            self.offstudy_model = self.model_validator(
                model=offstudy_model, required=True,
                visit_schedule_name=visit_schedule_name).model
        except ModelValidatorError as e:
            raise ModelValidatorError(
                f'offstudy model: {e}. See {visit_schedule_name}') from e

        try:
            self.enrollment_model = self.enrollment_model_validator(
                model=enrollment_model, required=True,
                visit_schedule_name=visit_schedule_name).model
        except EnrollmentModelValidatorError as e:
            raise ModelValidatorError(
                f'enrollment model: {e}. See {visit_schedule_name}') from e

        try:
            self.disenrollment_model = self.disenrollment_model_validator(
                model=disenrollment_model, required=True,
                visit_schedule_name=visit_schedule_name).model
        except DisenrollmentModelValidatorError as e:
            raise ModelValidatorError(
                f'disenrollment model: {e}. See {visit_schedule_name}') from e
