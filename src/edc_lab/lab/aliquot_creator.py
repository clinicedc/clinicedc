from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from edc_protocol import Protocol

from ..identifiers import AliquotIdentifier


class AliquotCreatorError(Exception):
    pass


class AliquotCreator:
    """A class that creates an aliquot.

    Aliquot is either a primary aliquot (is_primary=True) or
    a child aliquot (is_primary=False).
    """

    aliquot_identifier_cls = AliquotIdentifier
    aliquot_model = "edc_lab.aliquot"

    def __init__(
        self,
        parent_identifier=None,
        identifier_prefix=None,
        requisition_identifier=None,
        subject_identifier=None,
        is_primary=None,
    ):
        self.aliquot_model_cls = django_apps.get_model(self.aliquot_model)
        self.requisition_identifier = requisition_identifier
        self.subject_identifier = subject_identifier
        if not parent_identifier and not is_primary:
            raise AliquotCreatorError(
                "Cannot create child aliquot without parent aliquot identifier. "
                f"Got is_primary={is_primary}."
            )
        else:
            self.parent_identifier = parent_identifier
        self.identifier_prefix = (
            identifier_prefix or f"{Protocol().protocol_number}{self.requisition_identifier}"
        )
        if is_primary:
            self.parent_segment = None
        else:
            self.parent_segment = self.parent_identifier[-4:]
        self.is_primary = is_primary

    def create(self, count=None, aliquot_type=None):
        """Returns a newly created or existing non-primary
        aliquot model instance.
        """
        try:
            aliquot = self.aliquot_model_cls.objects.get(
                aliquot_type=aliquot_type,
                count=count,
                parent_identifier=self.parent_identifier,
                is_primary=False,
            )
        except ObjectDoesNotExist:
            aliquot = self._create(
                aliquot_type=aliquot_type,
                count=count,
                parent_identifier=self.parent_identifier,
            )
        return aliquot

    def create_primary(self, aliquot_type=None):
        """Returns an existing or newly created primary
        aliquot model instance.
        """
        try:
            aliquot = self.aliquot_model_cls.objects.get(
                Q(identifier_prefix=self.identifier_prefix)
                | Q(requisition_identifier=self.requisition_identifier),
                is_primary=True,
            )
        except ObjectDoesNotExist:
            aliquot = self._create(count=1, aliquot_type=aliquot_type)
        return aliquot

    def _create(self, parent_identifier=None, count=None, aliquot_type=None):
        """Returns a newly created aliquot."""
        aliquot_identifier_obj = self.aliquot_identifier_cls(
            count=count,
            numeric_code=aliquot_type.numeric_code,
            identifier_prefix=self.identifier_prefix,
            parent_segment=self.parent_segment,
        )

        parent_identifier = parent_identifier or aliquot_identifier_obj.identifier

        aliquot = self.aliquot_model_cls.objects.create(
            aliquot_identifier=aliquot_identifier_obj.identifier,
            aliquot_type=aliquot_type.name,
            alpha_code=aliquot_type.alpha_code,
            count=count,
            numeric_code=aliquot_type.numeric_code,
            parent_identifier=parent_identifier,
            identifier_prefix=self.identifier_prefix,
            is_primary=True if self.is_primary else False,
            requisition_identifier=self.requisition_identifier,
            subject_identifier=self.subject_identifier,
        )
        return aliquot
