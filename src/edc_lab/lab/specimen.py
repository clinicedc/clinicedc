from django.apps import apps as django_apps

from edc_constants.constants import YES

from .aliquot_object import AliquotObject


class SpecimenError(Exception):
    pass


class Specimen:

    def __init__(self, requisition=None, requisition_pk=None, **kwargs):
        app_config = django_apps.get_app_config('edc_lab')
        self.aliquot_model = django_apps.get_model(
            *app_config.aliquot_model.split('.'))
        self.requisition_model = django_apps.get_model(
            *app_config.requisition_model.split('.'))
        self._aliquots = None
        self._identifier_prefix = None
        self._primary_aliquot = None
        self.requisition = requisition or self.requisition_model.objects.get(
            pk=requisition_pk)
        if not self.requisition.is_drawn == YES:
            raise SpecimenError('Specimen was not drawn')
        else:
            if not self.requisition.identifier_prefix:
                self.requisition.identifier_prefix = self.identifier_prefix
                self.requisition.primary_aliquot_identifier = self.primary_aliquot.aliquot_identifier
                self.requisition.save()

    @property
    def aliquots(self):
        """Returns a queryset of wrapped aliquots.
        """
        if not self._aliquots:
            self._aliquots = [AliquotObject(obj) for obj in self.aliquot_model.objects.filter(
                identifier_prefix=self.identifier_prefix)]
        return self._aliquots

    @property
    def aliquot_count(self):
        return len(self.aliquots)

    @property
    def primary_aliquot(self):
        """Returns a wrapped aliquot object of the "primary" aliquot model
        instance.

        The aliquot model instance will be created if one does not
        already exist.
        """
        if not self._primary_aliquot:

            try:
                obj = self.aliquot_model.objects.get(
                    identifier_prefix=self.requisition.identifier_prefix,
                    is_primary=True)
            except self.aliquot_model.DoesNotExist:
                obj = self.aliquot_model.objects.create(
                    identifier_prefix=self.identifier_prefix,
                    aliquot_type=self.requisition.panel_object.aliquot_type.name,
                    numeric_code=self.requisition.panel_object.aliquot_type.numeric_code,
                    alpha_code=self.requisition.panel_object.aliquot_type.alpha_code,
                    aliquot_identifier=self.primary_aliquot_identifier,
                    subject_identifier=self.requisition.subject_identifier,
                    requisition_identifier=self.requisition.requisition_identifier,
                    count=0,
                    medium_count=self.requisition.item_count,
                    medium=self.requisition.item_type,
                    is_primary=True)
            self._primary_aliquot = AliquotObject(obj)
        return self._primary_aliquot

    @property
    def identifier_prefix(self):
        if not self._identifier_prefix:
            edc_protocol_app_config = django_apps.get_app_config(
                'edc_protocol')
            identifier_prefix = '{protocol_number}{requisition_identifier}'.format(
                protocol_number=edc_protocol_app_config.protocol_number,
                requisition_identifier=self.requisition.requisition_identifier)
            if len(identifier_prefix) != (18 - 8):
                raise SpecimenError(
                    'Invalid identifier prefix {}. Got length == {}. '
                    'Expected 10.'.format(
                        identifier_prefix, len(identifier_prefix)))
            self._identifier_prefix = identifier_prefix
        return self._identifier_prefix

    @property
    def primary_aliquot_identifier(self):
        return (self.identifier_prefix
                + '0000'
                + self.requisition.panel_object.aliquot_type.numeric_code
                + '01')
