from django.core.exceptions import FieldError


class DashboardError(Exception):
    pass


class DashboardFieldError(FieldError):
    pass
