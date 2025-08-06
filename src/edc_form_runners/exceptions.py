__all__ = [
    "FormRunnerError",
    "FormRunnerModelAdminNotFound",
    "FormRunnerImproperlyConfigured",
    "FormRunnerRegisterError",
]


class FormRunnerError(Exception):
    pass


class FormRunnerModelAdminNotFound(Exception):
    pass


class FormRunnerModelFormNotFound(Exception):
    pass


class FormRunnerImproperlyConfigured(Exception):
    pass


class FormRunnerRegisterError(Exception):
    pass
