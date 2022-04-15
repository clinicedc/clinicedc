class PrescriptionError(Exception):
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
