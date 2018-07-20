from django.apps import apps as django_apps
from edc_constants.constants import YES

from ..identifiers import Prefix as IdentifierPrefix
from .aliquot_creator import AliquotCreator
from .primary_aliquot import PrimaryAliquot
from .specimen_processor import SpecimenProcessor


class SpecimenNotDrawnError(Exception):
    pass


class Specimen:

    """A class that represents a collected specimen and it's aliquots
    given the original requisition.

    The primary aliquot will be created if it does not already exist.
    """

    aliquot_creator_cls = AliquotCreator
    aliquot_model = 'edc_lab.aliquot'
    identifier_prefix_cls = IdentifierPrefix
    primary_aliquot_cls = PrimaryAliquot
    specimen_processor_cls = SpecimenProcessor

    def __init__(self, requisition=None):

        self.requisition = requisition

        if not self.requisition.is_drawn == YES:
            raise SpecimenNotDrawnError(
                f'Specimen not drawn. Got \'{requisition}\'')

        self.aliquot_type = self.requisition.panel_object.aliquot_type

        if not self.requisition.identifier_prefix:
            self.requisition.identifier_prefix = self.primary_aliquot.identifier_prefix
            self.requisition.primary_aliquot_identifier = (
                self.primary_aliquot.aliquot_identifier)
            self.requisition.save()

    @property
    def primary_aliquot(self):
        """Returns a primary aliquot model instance after
        getting or creating one.
        """
        primary_aliquot_obj = self.primary_aliquot_cls(
            aliquot_creator_cls=self.aliquot_creator_cls,
            aliquot_type=self.aliquot_type,
            identifier_prefix=self.identifier_prefix,
            requisition_identifier=self.requisition.requisition_identifier,
            subject_identifier=self.requisition.subject_identifier)
        return primary_aliquot_obj.object

    def process(self):
        """Returns a list of aliquots after getting or creating
        the aliquots according to the processing profile.
        """
        specimen_processor = self.specimen_processor_cls(
            aliquot_creator_cls=self.aliquot_creator_cls,
            identifier_prefix=self.identifier_prefix,
            model_obj=self.primary_aliquot,
            processing_profile=self.requisition.panel_object.processing_profile)
        return specimen_processor.create()

    @property
    def aliquots(self):
        aliquot_model_cls = django_apps.get_model(self.aliquot_model)
        return aliquot_model_cls.objects.filter(
            identifier_prefix=self.identifier_prefix)

    @property
    def identifier_prefix(self):
        """Returns an identifier prefix string based on the
        requisition_identifier.
        """
        return self.identifier_prefix_cls(
            protocol_number=self.requisition.get_protocol_number(),
            requisition_identifier=self.requisition.requisition_identifier)
