class PrescriptionError(Exception):
    pass


class PrescriptionRefillError(Exception):
    pass


class ActivePrescriptionRefillOverlap(Exception):
    pass


class ActivePrescriptionRefillExists(Exception):
    pass


class NextPrescriptionRefillError(Exception):
    pass
