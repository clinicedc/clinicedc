class NotConsentedError(Exception):
    pass


class ConsentVersionSequenceError(Exception):
    pass


class ConsentError(Exception):
    pass


class ConsentDefinitionError(Exception):
    pass


class ConsentDefinitionModelError(Exception):
    pass


class ConsentDefinitionDoesNotExist(Exception):
    pass


class ConsentDefinitionValidityPeriodError(Exception):
    pass


class AlreadyRegistered(Exception):
    pass


class SiteConsentError(Exception):
    pass


class ConsentDefinitionNotConfiguredForUpdate(Exception):
    pass


class ConsentExtensionDefinitionError(Exception):
    pass


class ConsentExtensionDefinitionModelError(Exception):
    pass
