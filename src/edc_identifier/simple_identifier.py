import random
from typing import Any, Optional, Type

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from edc_utils import get_utcnow

from .utils import convert_to_human_readable


class DuplicateIdentifierError(Exception):
    pass


class IdentifierError(Exception):
    pass


class SimpleIdentifier:
    random_string_length: int = 5
    template: str = "{device_id}{random_string}"
    identifier_prefix: str = None

    def __init__(
        self,
        template: Optional[str] = None,
        random_string_length: Optional[int] = None,
        identifier_prefix: Optional[str] = None,
        device_id: Optional[str] = None,
    ) -> None:
        self._identifier: Optional[str] = None
        self.template = template or self.template
        self.random_string_length = random_string_length or self.random_string_length
        self.device_id = device_id or django_apps.get_app_config("edc_device").device_id
        self.identifier_prefix = identifier_prefix or self.identifier_prefix

    def __str__(self) -> str:
        return self.identifier

    @property
    def identifier(self) -> str:
        if not self._identifier:
            self._identifier = self.template.format(
                device_id=self.device_id, random_string=self.random_string
            )
            if self.identifier_prefix:
                self._identifier = f"{self.identifier_prefix}{self._identifier}"
        return self._identifier

    @property
    def random_string(self) -> str:
        return "".join(
            [
                random.choice("ABCDEFGHKMNPRTUVWXYZ2346789")  # nosec B311
                for _ in range(self.random_string_length)
            ]
        )


class SimpleTimestampIdentifier(SimpleIdentifier):
    timestamp_format: str = "%y%m%d%H%M%S%f"
    timestamp_length: int = 14

    @property
    def identifier(self) -> str:
        if not self._identifier:
            self._identifier = self.template.format(
                device_id=self.device_id,
                timestamp=timezone.localtime().strftime(self.timestamp_format)[
                    : self.timestamp_length
                ],
                random_string=self.random_string,
            )
            if self.identifier_prefix:
                self._identifier = f"{self.identifier_prefix}{self._identifier}"
        return self._identifier


class SimpleSequentialIdentifier:
    prefix: Optional[str] = None

    def __init__(self):
        sequence: int = int(get_utcnow().timestamp())
        random_number: int = random.choice(range(1000, 9999))  # nosec B311
        sequence: str = f"{sequence}{random_number}"
        chk: int = int(sequence) % 11
        self.identifier: str = f'{self.prefix or ""}{sequence}{chk}'

    def __str__(self) -> str:
        return self.identifier


class SimpleUniqueIdentifier:

    """Usage:

    class ManifestIdentifier(Identifier):
        random_string_length = 9
        identifier_attr = 'manifest_identifier'
        template = 'M{device_id}{random_string}'
    """

    random_string_length: int = 5
    identifier_type: str = "simple_identifier"
    identifier_attr: str = "identifier"
    model: str = "edc_identifier.identifiermodel"
    template: str = "{device_id}{random_string}"
    identifier_prefix: Optional[str] = None
    identifier_cls = SimpleIdentifier
    make_human_readable: Optional[bool] = None

    def __init__(
        self,
        model: str = None,
        identifier_attr: Optional[str] = None,
        identifier_type: Optional[str] = None,
        identifier_prefix: Optional[str] = None,
        make_human_readable: Optional[bool] = None,
        linked_identifier: Optional[str] = None,
        protocol_number: Optional[str] = None,
        source_model: Optional[str] = None,
        subject_identifier: Optional[str] = None,
        site: Optional[Any] = None,
        site_id: Optional[str] = None,
    ):
        self._identifier: Optional[str] = None
        self.site_id = None
        self.model = model or self.model
        self.identifier_attr = identifier_attr or self.identifier_attr
        self.identifier_type = identifier_type or self.identifier_type
        self.identifier_prefix = identifier_prefix or self.identifier_prefix
        if self.identifier_prefix and len(self.identifier_prefix) != 2:
            raise IdentifierError(
                f"Expected identifier_prefix of length=2. Got {len(identifier_prefix)}"
            )
        self.make_human_readable = make_human_readable or self.make_human_readable
        self.device_id = django_apps.get_app_config("edc_device").device_id
        if site:
            self.site_id = site.id
        elif site_id:
            self.site_id = site_id
        opts = dict(
            sequence_number=1,
            linked_identifier=linked_identifier,
            protocol_number=protocol_number,
            model=source_model,
            subject_identifier=subject_identifier,
        )
        opts.update({self.identifier_attr: self.identifier})
        self.update_identifier_model(**opts)

    def __str__(self):
        return self.identifier

    @property
    def identifier(self) -> str:
        if not self._identifier:
            identifier = self._get_new_identifier()
            tries = 1
            while True:
                tries += 1
                try:
                    self.model_cls.objects.get(
                        identifier_type=self.identifier_type,
                        **{self.identifier_attr: identifier},
                    )
                except ObjectDoesNotExist:
                    break
                else:
                    identifier = self._get_new_identifier()
                if tries == len("ABCDEFGHKMNPRTUVWXYZ2346789") ** self.random_string_length:
                    raise DuplicateIdentifierError(
                        "Unable prepare a unique identifier, "
                        "all are taken. Increase the length of the random string"
                    )
            self._identifier = identifier
            if self.make_human_readable:
                self._identifier = convert_to_human_readable(identifier)
        return self._identifier

    def _get_new_identifier(self) -> str:
        """Returns a new identifier."""
        identifier_obj = self.identifier_cls(
            template=self.template,
            identifier_prefix=self.identifier_prefix,
            random_string_length=self.random_string_length,
            device_id=self.device_id,
        )
        return identifier_obj.identifier

    @property
    def model_cls(self) -> Type[models.Model]:
        return django_apps.get_model(self.model)

    def update_identifier_model(self, **kwargs) -> bool:
        """Attempts to update identifier_model and returns True (or instance)
        if successful else False if identifier already exists.
        """
        opts = dict(
            identifier=self.identifier,
            identifier_type=self.identifier_type,
            identifier_prefix=self.identifier_prefix,
            device_id=self.device_id,
            site_id=self.site_id,
        )
        opts.update(**kwargs)
        try:
            self.model_cls.objects.get(identifier=self.identifier)
        except ObjectDoesNotExist:
            return self.model_cls.objects.create(**opts)
        return False
