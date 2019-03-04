import random
import re

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from edc_utils import get_utcnow


class DuplicateIdentifierError(Exception):
    pass


class IdentifierError(Exception):
    pass


def make_human_readable(identifier):
    return "-".join(re.findall(".{1,4}", identifier))


class SimpleIdentifier:

    random_string_length = 5
    template = "{device_id}{random_string}"
    identifier_prefix = None

    def __init__(
        self,
        template=None,
        random_string_length=None,
        identifier_prefix=None,
        device_id=None,
    ):
        self._identifier = None
        self.template = template or self.template
        self.random_string_length = random_string_length or self.random_string_length
        self.device_id = device_id or django_apps.get_app_config("edc_device").device_id
        self.identifier_prefix = identifier_prefix or self.identifier_prefix

    def __str__(self):
        return self.identifier

    @property
    def identifier(self):
        if not self._identifier:
            self._identifier = self.template.format(
                device_id=self.device_id, random_string=self.random_string
            )
            if self.identifier_prefix:
                self._identifier = f"{self.identifier_prefix}{self._identifier}"
        return self._identifier

    @property
    def random_string(self):
        return "".join(
            [
                random.choice("ABCDEFGHKMNPRTUVWXYZ2346789")
                for _ in range(self.random_string_length)
            ]
        )


class SimpleTimestampIdentifier(SimpleIdentifier):

    timestamp_format = "%y%m%d%H%M%S%f"
    timestamp_length = 14

    @property
    def identifier(self):
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

    prefix = None

    def __init__(self):
        sequence = int(get_utcnow().timestamp())
        random_number = random.choice(range(1000, 9999))
        sequence = f"{sequence}{random_number}"
        chk = int(sequence) % 11
        self.identifier = f'{self.prefix or ""}{sequence}{chk}'

    def __str__(self):
        return self.identifier


class SimpleUniqueIdentifier:

    """Usage:

        class ManifestIdentifier(Identifier):
            random_string_length = 9
            identifier_attr = 'manifest_identifier'
            template = 'M{device_id}{random_string}'
    """

    random_string_length = 5
    identifier_type = "simple_identifier"
    identifier_attr = "identifier"
    model = "edc_identifier.identifiermodel"
    template = "{device_id}{random_string}"
    identifier_prefix = None
    identifier_cls = SimpleIdentifier
    make_human_readable = None

    def __init__(
        self,
        model=None,
        identifier_attr=None,
        identifier_type=None,
        identifier_prefix=None,
        make_human_readable=None,
        linked_identifier=None,
        protocol_number=None,
        source_model=None,
        subject_identifier=None,
    ):
        self._identifier = None
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
        self.model_cls.objects.create(
            identifier_type=self.identifier_type,
            sequence_number=1,
            device_id=self.device_id,
            linked_identifier=linked_identifier,
            protocol_number=protocol_number,
            model=source_model,
            subject_identifier=subject_identifier,
            **{self.identifier_attr: self.identifier},
        )

    def __str__(self):
        return self.identifier

    @property
    def identifier(self):
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
                if (
                    tries
                    == len("ABCDEFGHKMNPRTUVWXYZ2346789") ** self.random_string_length
                ):
                    raise DuplicateIdentifierError(
                        "Unable prepare a unique identifier, "
                        "all are taken. Increase the length of the random string"
                    )
            self._identifier = identifier
            if self.make_human_readable:
                self._identifier = make_human_readable(identifier)
        return self._identifier

    def _get_new_identifier(self):
        """Returns a new identifier.
        """
        identifier_obj = self.identifier_cls(
            template=self.template,
            identifier_prefix=self.identifier_prefix,
            random_string_length=self.random_string_length,
            device_id=self.device_id,
        )
        return identifier_obj.identifier

    @property
    def model_cls(self):
        return django_apps.get_model(self.model)
