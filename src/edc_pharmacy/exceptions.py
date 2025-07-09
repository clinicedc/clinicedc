class ActivePrescriptionRefillOverlap(Exception):
    pass


class RefillError(Exception):
    pass


class ActiveRefillAlreadyExists(Exception):
    pass


class NextRefillError(Exception):
    pass


class NextStudyMedicationError(Exception):
    pass


class InsufficientQuantityError(Exception):
    pass


class PackagingSidMismatchError(Exception):
    pass


class PackagingSubjectIdentifierMismatchError(Exception):
    pass


class PackagingLotNumberMismatchError(Exception):
    pass


class PrescriptionAlreadyExists(Exception):
    pass


class PrescriptionError(Exception):
    pass


class PrescriptionExpired(Exception):
    pass


class RefillAlreadyExists(Exception):
    pass


class PrescriptionNotStarted(Exception):
    pass


class RefillCreatorError(Exception):
    pass


class RefillEndDatetimeError(Exception):
    pass


class StudyMedicationError(Exception):
    pass


class StockError(Exception):
    pass


class InsufficientStockError(Exception):
    pass


class InvalidContainer(Exception):
    pass


class ReceiveError(Exception):
    pass


class RepackError(Exception):
    pass


class RepackRequestError(Exception):
    pass


class ProcessStockRequestError(Exception):
    pass


class StockRequestError(Exception):
    pass


class ChecksumError(Exception):
    pass


class AllocationError(Exception):
    pass


class OrderItemError(Exception):
    pass


class ReceiveItemError(Exception):
    pass


class StockRequestItemError(Exception):
    pass


class LotError(Exception):
    pass


class StockTransferError(Exception):
    pass


class AssignmentError(Exception):
    pass


class StockTransferConfirmationError(Exception):
    pass


class StorageBinError(Exception):
    pass


class ConfirmAtSiteError(Exception):
    pass
