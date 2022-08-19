from typing import Any

from .randomizer import Randomizer
from .site_randomizers import site_randomizers


class RegisterRandomizerError(Exception):
    pass


def register(site=None, **kwargs) -> Any:  # noqa
    """Registers a randomizer class."""
    site = site or site_randomizers

    def _register_randomizer_cls_wrapper(randomizer_cls: Any) -> Any:
        if not issubclass(randomizer_cls, (Randomizer,)):
            raise RegisterRandomizerError(
                f"Wrapped class must a Randomizer class. Got {randomizer_cls}"
            )
        site.register(randomizer_cls)
        return randomizer_cls

    return _register_randomizer_cls_wrapper
