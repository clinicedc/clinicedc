from django.apps import apps as django_apps

from edc_identifier.models import IdentifierModel

edc_device_app_config = django_apps.get_app_config('edc_device')
edc_protocol_app_config = django_apps.get_app_config('edc_protocol')


class InfantIdentifierError(Exception):
    pass


class InfantIdentifier:
    def __init__(self, model=None, maternal_identifier=None, birth_order=None,
                 live_infants=None, identifier=None, template=None,
                 create_registration=None, **kwargs):
        subject_type = 'infant'
        template = template or '{maternal_identifier}-{infant_suffix}'
        create_registration = (
            True if create_registration is None else create_registration)
        if identifier:
            identifier_model = IdentifierModel.objects.get(
                identifier=identifier)
            self.identifier = identifier_model.identifier
        elif not maternal_identifier:
            self.identifier = None
        else:
            try:
                IdentifierModel.objects.get(
                    identifier=maternal_identifier.identifier)
            except IdentifierModel.DoesNotExist:
                raise InfantIdentifierError(
                    'Unable to allocate infant identifier. Maternal_identifier '
                    f'{maternal_identifier.identifier} does not exist.')
            if birth_order > live_infants:
                raise InfantIdentifierError(
                    f'Unable to allocate infant identifier. Birth order cannot be '
                    f'{birth_order} if number of live infants is {live_infants}.')
            infant_suffix = self.infant_suffix(live_infants) + birth_order
            self.identifier = template.format(
                maternal_identifier=maternal_identifier.identifier,
                infant_suffix=infant_suffix)
            IdentifierModel.objects.create(
                name=self.label,
                sequence_number=infant_suffix,
                identifier=self.identifier,
                linked_identifier=maternal_identifier.identifier,
                protocol_number=edc_protocol_app_config.protocol_number,
                device_id=edc_device_app_config.device_id,
                model=model,
                study_site=maternal_identifier.site_code,
                subject_type=subject_type)
            if create_registration:
                RegisteredSubject = django_apps.get_app_config(
                    'edc_registration').model
                obj = RegisteredSubject.objects.get(
                    subject_identifier=maternal_identifier.identifier)
                first_name = 'Baby{}{}'.format(
                    birth_order + 1, (obj.last_name or 'UNKNOWN').lower().title())
                RegisteredSubject.objects.create(
                    subject_identifier=self.identifier,
                    subject_type=subject_type,
                    study_site=maternal_identifier.site_code,
                    relative_identifier=maternal_identifier.identifier,
                    first_name=kwargs.get('first_name', first_name),
                    initials=kwargs.get('initials', None),
                    registration_status=kwargs.get(
                        'registration_status', 'DELIVERED'),
                    registration_datetime=kwargs.get('registration_datetime', None))

    def __str__(self):
        return self.identifier

    @property
    def label(self):
        return 'infantidentifier'

    def infant_suffix(self, live_infants):
        if live_infants == 1:
            infant_suffix = 10  # singlet 10
        elif live_infants == 2:
            infant_suffix = 25  # twins 25,26
        elif live_infants == 3:
            infant_suffix = 36  # triplets 36,37,38
        elif live_infants == 4:
            infant_suffix = 47  # quadruplets 47,48,49,50
        elif live_infants == 5:
            infant_suffix = 58  # quintuplets 58, 59, 60, 61, 62
        else:
            raise InfantIdentifierError(
                f'Unable to allocate infant identifier. Ensure number of infants '
                f'is greater than 0 and less than or equal to 5. '
                f'You wrote {live_infants}.')
        return infant_suffix

    @classmethod
    def reverse_infant_suffix(cls, identifier):
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
            raise InfantIdentifierError('Unable to reverse infant identifier.')
        return birth_order, live_infants
