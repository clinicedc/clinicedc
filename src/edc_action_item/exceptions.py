from django.core.exceptions import ValidationError


class SubjectDoesNotExist(Exception):
    pass


class ActionClassNotDefined(Exception):
    pass


class ActionItemError(Exception):
    pass


class ActionTypeError(Exception):
    pass


class SingletonActionItemError(Exception):
    pass


class ActionError(ValidationError):
    pass
