from django.db.models import Q

from ..identifiers import AliquotIdentifier, AliquotIdentifierLengthError


class PrimaryAliquotError(Exception):
    pass


class PrimaryAliquotPrefixError(Exception):
    pass


class PrimaryAliquot:

    """A class that gets or creates the primary aliquot.
    """

    aliquot_identifier_cls = AliquotIdentifier

    def __init__(self, subject_identifier=None, requisition_identifier=None,
                 identifier_prefix=None, aliquot_type=None,
                 aliquot_model=None, **kwargs):
        self.aliquot_type = aliquot_type
        self.aliquot_model = aliquot_model
        self.requisition_identifier = requisition_identifier
        self.subject_identifier = subject_identifier
        self.identifier_prefix = identifier_prefix

        try:
            model_obj = self.aliquot_model.objects.get(
                Q(identifier_prefix=self.identifier_prefix) |
                Q(requisition_identifier=self.requisition_identifier),
                is_primary=True)
            self.identifier = model_obj.aliquot_identifier
        except self.aliquot_model.DoesNotExist:
            model_obj = self.create_primary(**kwargs)
            self.identifier = model_obj.aliquot_identifier
        self.object = model_obj

        self.identifier = self.object.aliquot_identifier

    def __str__(self):
        return self.object.aliquot_identifier

    def create_primary(self, **kwargs):
        try:
            aliquot_identifier_obj = self.aliquot_identifier_cls(
                numeric_code=self.aliquot_type.numeric_code,
                prefix=self.identifier_prefix, **kwargs)
        except AliquotIdentifierLengthError as e:
            raise PrimaryAliquotError(e) from e
        options = dict(
            identifier_prefix=self.identifier_prefix,
            aliquot_type=self.aliquot_type.name,
            numeric_code=self.aliquot_type.numeric_code,
            alpha_code=self.aliquot_type.alpha_code,
            aliquot_identifier=str(aliquot_identifier_obj),
            subject_identifier=self.subject_identifier,
            requisition_identifier=self.requisition_identifier,
            count=0,
            is_primary=True)
        return self.aliquot_model.objects.create(**options)
