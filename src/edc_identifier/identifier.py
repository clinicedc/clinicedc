from __future__ import annotations

import re

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from .exceptions import IdentifierError
from .models import IdentifierModel


class Identifier:
    name = "identifier"
    identifier_model_cls = IdentifierModel
    identifier_pattern = "^\d+$"  # noqa
    prefix_pattern: str | None = None
    prefix: str | None = None
    seed: str = "0"
    separator: str | None = None

    def __init__(self, last_identifier: str | None = None, prefix: str | None = None) -> None:
        self.identifier_as_list: list = []
        self.prefix: str = prefix or self.prefix or ""
        edc_device_app_config = django_apps.get_app_config("edc_device")
        self.device_id = edc_device_app_config.device_id
        self.identifier = (
            last_identifier or self.last_identifier or f"{self.prefix}{self.seed}"
        )
        self.prefix_pattern = f"^{self.prefix}$"
        self.identifier_pattern = self.prefix_pattern[:-1] + self.identifier_pattern[1:]
        if self.identifier:
            self.validate_identifier_pattern(self.identifier)
        self.next_identifier()

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.identifier}')"

    def __str__(self):
        return self.identifier

    def __next__(self):
        self.next_identifier()
        return self.identifier

    def next(self):
        return self.__next__()

    def next_identifier(self):
        """Sets the next identifier and updates the identifier model."""
        identifier = self.remove_separator(self.identifier)
        identifier = self.increment(identifier)
        self.identifier = self.insert_separator(identifier)
        self.validate_identifier_pattern(self.identifier)
        self.update_identifier_model()

    @staticmethod
    def increment(identifier: int | str):
        return str(int(identifier or 0) + 1)

    def validate_identifier_pattern(self, identifier, pattern=None, error_msg=None):
        pattern = pattern or self.identifier_pattern
        try:
            identifier = re.match(pattern, identifier).group()
        except AttributeError:
            error_msg = error_msg or (
                "Invalid identifier format for pattern "
                f"{pattern}. Got identifier='{identifier}'"
            )
            raise IdentifierError(error_msg)
        return identifier

    @property
    def identifier_prefix(self):
        """Returns the prefix extracted from the identifier using
        the prefix_pattern.
        """
        if not self.prefix_pattern:
            return None
        return re.match(self.prefix_pattern[:-1], self.identifier).group()

    def update_identifier_model(self) -> bool:
        """Attempts to update identifier_model and returns True (or instance)
        if successful else False if identifier already exists.
        """
        try:
            self.identifier_model_cls.objects.get(identifier=self.identifier)
        except ObjectDoesNotExist:
            return self.identifier_model_cls.objects.create(
                identifier=self.identifier,
                identifier_type=self.name,
                identifier_prefix=self.identifier_prefix,
                device_id=self.device_id,
            )
        return False

    @property
    def last_identifier(self):
        """Returns the last identifier in the identifier model."""
        try:
            instance = self.identifier_model_cls.objects.filter(
                identifier_type=self.name
            ).last()
            return instance.identifier
        except AttributeError:
            return None

    def remove_separator(self, identifier):
        """Returns the identifier after removing the separator.

        The identifier is split into a list by separator and
        saved  as `identifier_as_list`.
        """
        if not identifier:
            return identifier
        else:
            self.identifier_as_list = identifier.split(self.separator)
            return "".join(self.identifier_as_list)

    def insert_separator(self, identifier):
        """Returns the identifier by reinserting the separator."""
        if not self.identifier_as_list:
            self.identifier_as_list = [identifier]
        start = 0
        items = []
        for item in self.identifier_as_list:
            items.append(identifier[start : start + len(item)])
            start += len(item)
        identifier = (self.separator or "").join(items)
        return identifier
