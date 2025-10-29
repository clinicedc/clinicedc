class FormulaError(Exception):
    pass


class GradeReferenceError(Exception):
    pass


class LimitsNormalParseError(Exception):
    pass


class ValueReferenceError(Exception):
    pass


class SiteReportablesError(Exception):
    pass


class AlreadyRegistered(Exception):  # noqa: N818
    pass


class ReferenceRangeCollectionError(Exception):
    pass


class ValueBoundryError(Exception):
    pass


class NotEvaluated(Exception):  # noqa: N818
    pass


class BoundariesOverlap(Exception):  # noqa: N818
    pass
