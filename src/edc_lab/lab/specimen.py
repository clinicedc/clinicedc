from django.apps import apps as django_apps

from edc_constants.constants import YES

from ..identifiers import Prefix, AliquotIdentifier
from .specimen_processor import SpecimenProcessor
from .primary_aliquot import PrimaryAliquot
from .aliquot_creator import AliquotCreator


class SpecimenNotDrawnError(Exception):
    pass


class Specimen:

    """A class that represents a collected specimen and it's aliquots
    given the original requisition.

    The primary aliquot will be created if it does not already exist.

    """

    aliquot_creator_cls = AliquotCreator
    aliquot_identifier_cls = AliquotIdentifier
    specimen_processor_cls = SpecimenProcessor

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
            self.requisition.primary_aliquot_identifier = self.primary_aliquot.aliquot_identifier
            self.requisition.save()

    @property
    def primary_aliquot(self):
        """Returns a primary aliquot model instance after
        getting or creating one.
        """
        options = dict(
            aliquot_identifier_cls=self.aliquot_identifier_cls,
            aliquot_creator_cls=self.aliquot_creator_cls,
            aliquot_model=self.aliquot_model,
            aliquot_type=self.aliquot_type,
            count_padding=self.count_padding,
            identifier_prefix=self.identifier_prefix,
            identifier_length=self.identifier_length,
            requisition_identifier=self.requisition.requisition_identifier,
            subject_identifier=self.requisition.subject_identifier)
        primary_aliquot_obj = self.primary_aliquot_cls(**options)
        return primary_aliquot_obj.object

    def process(self):
        specimen_processor = self.specimen_processor_cls(
            aliquot_identifier_cls=self.aliquot_identifier_cls,
            aliquot_creator_cls=self.aliquot_creator_cls,
            count_padding=self.count_padding,
            identifier_length=self.identifier_length,
            identifier_prefix=self.identifier_prefix,
            model_obj=self.primary_aliquot,
            processing_profile=self.requisition.panel_object.processing_profile,
            subject_identifier=self.requisition.subject_identifier
        )
        return specimen_processor.create()

    @property
    def aliquots(self):
        return self.aliquot_model.objects.filter(
            identifier_prefix=self.identifier_prefix)

    @property
    def identifier_prefix(self):
        """Returns an identifier prefix string based on the
        requisition_identifier.
        """
        prefix_obj = self.prefix_cls(
            length=self.prefix_length,
            protocol_number=self.requisition.protocol_number,
            requisition_identifier=self.requisition.requisition_identifier,
            template=self.prefix_template,
        )
        return str(prefix_obj)
