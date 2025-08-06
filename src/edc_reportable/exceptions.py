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


class AlreadyRegistered(Exception):
    pass


class ReferenceRangeCollectionError(Exception):
    pass


class ValueBoundryError(Exception):
    pass


class NotEvaluated(Exception):
    pass


class BoundariesOverlap(Exception):
    pass


class ConversionNotHandled(Exception):
    pass
