class AppointmentStatusError(Exception):
    pass


class AppointmentBaselineError(Exception):
    pass


class AppointmentReasonUpdaterError(Exception):
    pass


class AppointmentReasonUpdaterCrfsExistsError(Exception):
    pass


class AppointmentReasonUpdaterRequisitionsExistsError(Exception):
    pass


class UnscheduledAppointmentError(Exception):
    pass


class AppointmentCreateError(Exception):
    pass


class AppointmentDatetimeError(Exception):
    pass


class UnknownVisitCode(Exception):
    pass


class AppointmentWindowError(Exception):
    pass


class AppointmentPermissionsRequired(Exception):
    pass


class AppointmentMissingValuesError(Exception):
    pass


class UnscheduledAppointmentNotAllowed(Exception):
    pass


class InvalidVisitCodeSequencesError(Exception):
    pass


class InvalidTimepointError(Exception):
    pass


class InvalidParentAppointmentStatusError(Exception):
    pass


class InvalidParentAppointmentMissingVisitError(Exception):
    pass


class AppointmentInProgressError(Exception):
    pass


class AppointmentCreatorError(Exception):
    pass
