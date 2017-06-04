from django.apps import apps as django_apps

from edc_constants.constants import YES

from .aliquot_wrapper import AliquotWrapper
from .primary_aliquot import PrimaryAliquot
from edc_lab.identifiers.prefix import Prefix


class SpecimenNotDrawnError(Exception):
    pass


class Specimen:

    aliquot_wrapper = AliquotWrapper

    primary_aliquot_cls = PrimaryAliquot
    identifier_length = 18
    count_padding = 2

    prefix_cls = Prefix
    prefix_template = '{protocol_number}{requisition_identifier}'
    prefix_length = 8

    def __init__(self, requisition=None, requisition_pk=None,
                 aliquot_model=None, requisition_model=None,
                 protocol=None, **kwargs):

        self._aliquots = None

        app_config = django_apps.get_app_config('edc_lab')

        if not requisition:
            requisition_model = requisition_model or django_apps.get_model(
                *app_config.requisition_model.split('.'))
            self.requisition = self.requisition_model.objects.get(
                pk=requisition_pk)
        else:
            self.requisition = requisition

        if not self.requisition.is_drawn == YES:
            raise SpecimenNotDrawnError(
                f'Specimen not drawn. Got \'{requisition}\'')

        if not self.requisition.identifier_prefix:
            prefix_obj = self.prefix_cls(
                template=self.prefix_template,
                length=self.prefix_length,
                protocol_number=self.requisition.protocol_number,
                requisition_identifier=self.self.requisition.requisition_identifier)
            aliquot_model = aliquot_model or django_apps.get_model(
                *app_config.aliquot_model.split('.'))
            primary_aliquot_obj = self.primary_aliquot_cls(
                aliquot_model=aliquot_model,
                identifier_prefix=str(prefix_obj),
                count_padding=self.count_padding,
                length=self.identifier_length)
            self.requisition.identifier_prefix = primary_aliquot_obj.identifier_prefix
            self.requisition.primary_aliquot_identifier = primary_aliquot_obj.identifier
            self.requisition.save()

    @property
    def aliquots(self):
        """Returns a queryset of wrapped aliquots.
        """
        if not self._aliquots:
            self._aliquots = [self.aliquot_wrapper(obj) for obj in self.aliquot_model.objects.filter(
                identifier_prefix=self.identifier_prefix)]
        return self._aliquots

    @property
    def aliquot_count(self):
        return len(self.aliquots)
