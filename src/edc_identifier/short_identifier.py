import random
import re

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from .checkdigit_mixins import LuhnOrdMixin
from .models import IdentifierModel


class ShortIdentifierError(Exception):
    pass


class ShortIdentifierPrefixError(Exception):
    pass


class ShortIdentifierPrefixPatternError(Exception):
    pass


class DuplicateIdentifierError(Exception):
    pass


class ShortIdentifier:

    name = "shortidentifier"
    template = "{prefix}{random_string}"
    random_string_pattern = r"[A-Z0-9]+"  # alhpanumeric
    random_string_length = 5
    prefix_pattern = r"^[0-9]{2}$"
    identifier_model_cls = IdentifierModel

    prefix = None
    seed = None

    checkdigit = LuhnOrdMixin()

    def __init__(
        self,
        name=None,
        prefix_pattern=None,
        prefix=None,
        template=None,
        random_string_length=None,
        random_string_pattern=None,
    ):
        self._last_random_string = None
        self.name = name or self.name
        self.template = template or self.template
        self.random_string_length = random_string_length or self.random_string_length
        self.random_string_pattern = random_string_pattern or self.random_string_pattern
        self.random_string_pattern = re.compile(self.random_string_pattern)
        self.prefix_pattern = prefix_pattern or self.prefix_pattern
        self.prefix = prefix or self.prefix or ""
        self.prefix = str(self.prefix)
        if self.prefix and not self.prefix_pattern:
            raise ShortIdentifierPrefixError(
                "Prefix declared without a corresponding pattern. "
                f"Got prefix='{self.prefix}', "
                f"prefix_pattern='{self.prefix_pattern}'."
            )

        if self.prefix_pattern:
            if not self.prefix_pattern.startswith("^") or not self.prefix_pattern.endswith(
                "$"
            ):
                raise ShortIdentifierPrefixPatternError(
                    f"Invalid prefix pattern. Got {self.prefix_pattern}."
                )
            self.prefix_pattern = re.compile(self.prefix_pattern)

        if not self.prefix and self.prefix_pattern:
            raise ShortIdentifierPrefixError(
                "Prefix does not match prefix pattern. Got prefix=None."
            )
        elif self.prefix and not self.prefix_pattern.match(self.prefix):
            raise ShortIdentifierPrefixError(
                "Prefix does not match prefix pattern. "
                f"Got '{self.prefix}' does not match "
                f"pattern '{self.prefix_pattern}'."
            )

        edc_device_app_config = django_apps.get_app_config("edc_device")
        self.device_id = edc_device_app_config.device_id

        self.identifier = self.get_identifier()

    def __str__(self):
        return self.identifier

    def get_identifier(self):
        """Returns a new unique identifier."""
        identifier = None
        allowed_chars = self.random_string_pattern.match("ABCDEFGHKMNPRTUVWXYZ2346789").group()
        max_tries = len(allowed_chars) ** (self.random_string_length + 1)
        tries = 0
        while not identifier:
            tries += 1
            random_string = "".join(
                [
                    random.choice(allowed_chars)  # nosec B311
                    for _ in range(self.random_string_length)
                ]
            )
            identifier = self.template.format(random_string=random_string, prefix=self.prefix)
            try:
                self.identifier_model_cls.objects.get(
                    identifier=identifier, identifier_type=self.name
                )
            except ObjectDoesNotExist:
                pass
            else:
                identifier = None
                if tries >= max_tries:
                    raise DuplicateIdentifierError(
                        "Unable prepare a unique requisition identifier, "
                        "all are taken. Increase the length of the random string. "
                        f"tries={tries}, max_tries={max_tries}."
                    )

        self.identifier_model_cls.objects.create(
            identifier=identifier,
            identifier_type=self.name,
            identifier_prefix=self.prefix,
            device_id=self.device_id,
        )
        return identifier
