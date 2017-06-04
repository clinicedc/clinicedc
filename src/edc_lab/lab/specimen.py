from django.apps import apps as django_apps

from edc_constants.constants import YES

from ..identifiers import Prefix
from .aliquot_wrapper import AliquotWrapper
from .primary_aliquot import PrimaryAliquot
from edc_lab.identifiers.aliquot_identifier import AliquotIdentifier
from edc_lab.lab.aliquot_type import AliquotType


class SpecimenNotDrawnError(Exception):
    pass


class Specimen:

    """A class that represents a collected specimen and it's aliquots
    given the original requisition.

    The primary aliquot will be created if it does not already exist.

    """

    aliquot_wrapper = AliquotWrapper

    aliquot_identifier_cls = AliquotIdentifier

    primary_aliquot_cls = PrimaryAliquot
    identifier_length = 18
    count_padding = 2

    prefix_cls = Prefix
    prefix_template = '{protocol_number}{requisition_identifier}'
    prefix_length = 10

    def __init__(self, requisition=None, requisition_pk=None,
                 aliquot_model=None, requisition_model=None, **kwargs):

        app_config = django_apps.get_app_config('edc_lab')
        self.aliquot_model = (aliquot_model or django_apps.get_model(
            *app_config.aliquot_model.split('.')))

        if not requisition:
            requisition_model = requisition_model or django_apps.get_model(
                *app_config.requisition_model.split('.'))
            self.requisition = requisition_model.objects.get(
                pk=requisition_pk)
        else:
            self.requisition = requisition

        if not self.requisition.is_drawn == YES:
            raise SpecimenNotDrawnError(
                f'Specimen not drawn. Got \'{requisition}\'')

        self.aliquot_type = self.requisition.panel_object.aliquot_type

        if not self.requisition.identifier_prefix:
            self.requisition.identifier_prefix = self.primary_aliquot.identifier_prefix
            self.requisition.primary_aliquot_identifier = self.primary_aliquot.identifier
            self.requisition.save()

        self.aliquots = [self.aliquot_wrapper(obj) for obj in self.aliquot_model.objects.filter(
            identifier_prefix=self.identifier_prefix)]

    @property
    def aliquot_count(self):
        return len(self.aliquots)

    @property
    def identifier_prefix(self):
        """Returns an identifier prefix string based on the
        requisition_identifier.
        """
        prefix_obj = self.prefix_cls(
            template=self.prefix_template,
            length=self.prefix_length,
            protocol_number=self.requisition.protocol_number,
            requisition_identifier=self.requisition.requisition_identifier)
        return str(prefix_obj)

    @property
    def primary_aliquot(self):
        """Returns a primary aliquot object after getting or creating
        the primary aliquot model instance.
        """
        return self.primary_aliquot_cls(
            aliquot_model=self.aliquot_model,
            aliquot_type=self.aliquot_type,
            identifier_prefix=self.identifier_prefix,
            count_padding=self.count_padding,
            length=self.identifier_length,
            aliquot_identifier_cls=AliquotIdentifier)
