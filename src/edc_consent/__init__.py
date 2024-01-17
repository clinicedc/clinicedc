from importlib.metadata import version

__version__ = version("edc_consent")
__all__ = [
    "site_consents",
    "ConsentDefinitionDoesNotExist",
    "ConsentDefinitionError",
    "ConsentError",
    "ConsentVersionSequenceError",
    "NotConsentedError",
]

from .exceptions import (
    ConsentDefinitionDoesNotExist,
    ConsentDefinitionError,
    ConsentError,
    ConsentVersionSequenceError,
    NotConsentedError,
)
from .site_consents import site_consents
