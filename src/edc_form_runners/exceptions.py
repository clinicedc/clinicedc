__all__ = [
    "FormRunnerError",
    "FormRunnerImproperlyConfigured",
    "FormRunnerModelAdminNotFound",
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
