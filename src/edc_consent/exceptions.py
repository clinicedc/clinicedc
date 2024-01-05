class ConsentDefinitionDoesNotExist(Exception):
    pass


class NotConsentedError(Exception):
    pass


class ConsentVersionSequenceError(Exception):
    pass


class ConsentError(Exception):
    pass
