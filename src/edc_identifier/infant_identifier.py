from django.apps import apps as django_apps
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from edc_registration.models import RegisteredSubject
from edc_utils import get_utcnow

from .models import IdentifierModel

edc_device_app_config = django_apps.get_app_config("edc_device")
edc_protocol_app_config = django_apps.get_app_config("edc_protocol")


def reverse_infant_suffix(identifier, birth_order, live_infants):
    infant_suffix = int(identifier[-2:])
    if infant_suffix == 10:
        birth_order, live_infants = 0, 1
    elif 25 <= infant_suffix <= 26:
        birth_order, live_infants = infant_suffix - 25, 2
    elif 36 <= infant_suffix <= 38:
        birth_order, live_infants = infant_suffix - 36, 3
    elif 47 <= infant_suffix <= 50:
        birth_order, infant_suffix = infant_suffix - 47, 4
    elif 58 <= infant_suffix <= 62:
        birth_order, infant_suffix = infant_suffix - 58, 5
    else:
        raise InfantIdentifierError("Unable to reverse infant identifier.")
    return birth_order, live_infants


class InfantIdentifierError(Exception):
    pass


class InfantIdentifier:

    subject_type = "infant"
    template = "{maternal_identifier}-{infant_suffix}"
    identifier_model_cls = IdentifierModel
    label = "infantidentifier"

    def __init__(
        self,
        maternal_identifier=None,
        requesting_model=None,
        birth_order=None,
        live_infants=None,
        template=None,
        first_name=None,
        initials=None,
        last_name=None,
        registration_status=None,
        registration_datetime=None,
        subject_type=None,
    ):
        self._first_name = first_name
        self._identifier = None
        self._infant_suffix = None
        # check maternal identifier
        try:
            rs = RegisteredSubject.objects.get(subject_identifier=maternal_identifier)
        except ObjectDoesNotExist:
            raise InfantIdentifierError(
                f"Failed to create infant identifier. Invalid maternal "
                f"identifier. Got {maternal_identifier}"
            )
        self.last_name = last_name or rs.last_name
        self.maternal_identifier = maternal_identifier
        self.birth_order = birth_order
        self.initials = initials
        self.live_infants = live_infants
        self.registration_datetime = registration_datetime or get_utcnow()
        self.registration_status = registration_status or "DELIVERED"
        self.requesting_model = requesting_model
        self.subject_type = subject_type or self.subject_type
        self.template = template or self.template

        self.identifier

    def __str__(self):
        return self.identifier

    @property
    def identifier(self):
        if not self._identifier:
            identifier = self.template.format(
                maternal_identifier=self.maternal_identifier,
                infant_suffix=self.infant_suffix,
            )
            try:
                self.identifier_model_cls.objects.get(identifier=identifier)
            except ObjectDoesNotExist:
                pass
            else:
                raise InfantIdentifierError(
                    f"Infant identifier unexpectedly exists. "
                    f"See model {self.identifier_model_cls._meta.label_lower}. "
                    f"Got {identifier}"
                )
            try:
                RegisteredSubject.objects.get(subject_identifier=identifier)
            except ObjectDoesNotExist:
                pass
            else:
                raise InfantIdentifierError(
                    f"Infant identifier unexpectedly exists. "
                    f"See {RegisteredSubject._meta.label_lower}. "
                    f"Got {identifier}"
                )
            # update identifier model
            self.identifier_model_cls.objects.create(
                name=self.label,
                sequence_number=self.infant_suffix,
                identifier=identifier,
                linked_identifier=self.maternal_identifier,
                protocol_number=edc_protocol_app_config.protocol_number,
                device_id=edc_device_app_config.device_id,
                model=self.requesting_model,
                site=Site.objects.get_current(),
                identifier_type=self.subject_type,
            )
            # update RegisteredSubject
            RegisteredSubject.objects.create(
                subject_identifier=identifier,
                subject_type=self.subject_type,
                site=Site.objects.get_current(),
                relative_identifier=self.maternal_identifier,
                first_name=self.first_name,
                initials=self.initials,
                registration_status=self.registration_status,
                registration_datetime=self.registration_datetime,
            )
            self._identifier = identifier
        return self._identifier

    @property
    def first_name(self):
        if not self._first_name:
            a = self.birth_order
            b = (self.last_name or "UNKNOWN").lower().title()
            self._first_name = f"Baby{a}{b}"
        return self._first_name

    @property
    def infant_suffix(self):
        if not self._infant_suffix:
            if not (0 < self.birth_order <= self.live_infants):
                raise InfantIdentifierError(
                    f"Unable to allocate infant identifier. Birth order cannot be "
                    f"{self.birth_order} if number of live infants is {self.live_infants}."
                )
            if self.live_infants == 1:
                suffix = 10  # singlet 10
            elif self.live_infants == 2:
                suffix = 25  # twins 25,26
            elif self.live_infants == 3:
                suffix = 36  # triplets 36,37,38
            elif self.live_infants == 4:
                suffix = 47  # quadruplets 47,48,49,50
            elif self.live_infants == 5:
                suffix = 58  # quintuplets 58, 59, 60, 61, 62
            else:
                raise InfantIdentifierError(
                    f"Unable to allocate infant identifier. Ensure number of infants "
                    f"is greater than 0 and less than or equal to 5. "
                    f"Got {self.live_infants}."
                )
            self._infant_suffix = suffix + (self.birth_order - 1)
        return self._infant_suffix
