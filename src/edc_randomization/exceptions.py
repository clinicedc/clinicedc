from django.core.exceptions import ValidationError


class InvalidAssignment(Exception):  # noqa: N818
    pass


class RandomizationListImportError(Exception):
    pass


class RandomizationListAlreadyImported(Exception):  # noqa: N818
    pass


class RandomizationListError(Exception):
    pass


class RegistryNotLoaded(Exception):  # noqa: N818
    pass


class NotRegistered(Exception):  # noqa: N818
    pass


class AlreadyRegistered(Exception):  # noqa: N818
    pass


class SiteRandomizerError(Exception):
    pass


class RandomizationListExporterError(Exception):
    pass


class SubjectNotRandomization(Exception):  # noqa: N818
    pass


class InvalidAssignmentDescriptionMap(Exception):  # noqa: N818
    pass


class RandomizationListFileNotFound(Exception):  # noqa: N818
    pass


class RandomizationListNotLoaded(Exception):  # noqa: N818
    pass


class RandomizationError(Exception):
    pass


class AlreadyRandomized(ValidationError):  # noqa: N818
    pass


class AllocationError(Exception):
    pass


class RegisterRandomizerError(Exception):
    pass


class RandomizationListModelError(Exception):
    pass
