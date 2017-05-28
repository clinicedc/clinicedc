from .disenrollment_validator import DisenrollmentValidator, DisenrollmentValidatorError
from .enrollment_validator import EnrollmentValidator, EnrollmentValidatorError


class ValidatorError(Exception):
    pass


class ModelsValidatorError(Exception):
    pass


class ModelsValidator:

    """A class that validates the configuration of model classes
    used by Schedule and VisitSchedule.
    """

    disenrollment_validator_cls = DisenrollmentValidator
    enrollment_validator_cls = EnrollmentValidator

    def __init__(self, visit_schedule_name=None, enrollment_model=None,
                 disenrollment_model=None, models=None, **kwargs):
        super().__init__(visit_schedule_name=visit_schedule_name, models=models)

        try:
            validator = self.enrollment_validator_cls(
                model=enrollment_model, required=True,
                visit_schedule_name=visit_schedule_name)
            self.enrollment_model = validator.get_and_validate_model()
        except EnrollmentValidatorError as e:
            raise EnrollmentValidatorError(
                f'{e}. See {visit_schedule_name}') from e

        try:
            validator = self.disenrollment_validator_cls(
                model=disenrollment_model, required=True,
                visit_schedule_name=visit_schedule_name)
            self.disenrollment_model = validator.get_and_validate_model()
        except DisenrollmentValidatorError as e:
            raise DisenrollmentValidatorError(
                f'{e}. See {visit_schedule_name}') from e
