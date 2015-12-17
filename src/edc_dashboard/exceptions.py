from django.core.exceptions import FieldError


class DashboardModelError(Exception):
    pass


class SearchError(Exception):
    pass


class SearchModelError(Exception):
    pass


class SearchAttributeError(Exception):
    pass


class SectionError(Exception):
    pass


class DashboardError(Exception):
    pass


class DashboardFieldError(FieldError):
    pass
