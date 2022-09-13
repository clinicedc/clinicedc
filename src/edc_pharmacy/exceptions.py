class PrescriptionError(Exception):
    pass


class PrescriptionNotStarted(Exception):
    pass


class PrescriptionExpired(Exception):
    pass


class PrescriptionAlreadyExists(Exception):
    pass


class ActivePrescriptionRefillOverlap(Exception):
    pass


class RefillError(Exception):
    pass


class RefillAlreadyExists(Exception):
    pass


class ActiveRefillAlreadyExists(Exception):
    pass


class NextRefillError(Exception):
    pass


class InsufficientQuantityError(Exception):
    pass


class PackagingSidMismatchError(Exception):
    pass


class PackagingSubjectIdentifierMismatchError(Exception):
    pass


class PackagingLotNumberMismatchError(Exception):
    pass
