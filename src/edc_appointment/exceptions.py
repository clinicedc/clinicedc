class AppointmentStatusError(Exception):
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
