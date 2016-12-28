class AlreadyRegistered(Exception):
    pass


class SiteConsentError(Exception):
    pass


class ConsentDoesNotExist(Exception):
    pass


class ConsentVersionError(Exception):
    pass


class ConsentMixinError(Exception):
    pass


class NotConsentedError(Exception):
    pass


class ConsentError(Exception):
    pass


class ConsentPeriodError(Exception):
    pass


class ConsentPeriodOverlapError(Exception):
    pass


class ConsentVersionSequenceError(Exception):
    pass
