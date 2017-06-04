from django.db.models import Q


class PrimaryAliquotError(Exception):
    pass


class PrimaryAliquotPrefixError(Exception):
    pass


class PrimaryAliquot:

    """A class that gets or creates the primary aliquot.
    """

    def __init__(self, subject_identifier=None, requisition_identifier=None,
                 identifier_prefix=None, aliquot_type=None,
                 aliquot_model=None, aliquot_creator_cls=None,
                 aliquot_identifier_cls=None, **kwargs):
        self.aliquot_type = aliquot_type
        self.aliquot_model = aliquot_model
        self.requisition_identifier = requisition_identifier
        self.subject_identifier = subject_identifier
        self.identifier_prefix = identifier_prefix
        self.subject_identifier = subject_identifier

        try:
            model_obj = self.aliquot_model.objects.get(
                Q(identifier_prefix=self.identifier_prefix) |
                Q(requisition_identifier=self.requisition_identifier),
                is_primary=True)
            self.identifier = model_obj.aliquot_identifier
        except self.aliquot_model.DoesNotExist:
            options = dict(
                aliquot_identifier_cls=aliquot_identifier_cls,
                aliquot_model=aliquot_model,
                identifier_prefix=self.identifier_prefix,
                is_primary=True,
                requisition_identifier=self.requisition_identifier,
                subject_identifier=self.subject_identifier,
                **kwargs)
            aliquot_creator = aliquot_creator_cls(**options)
            model_obj = aliquot_creator.create(aliquot_type=self.aliquot_type)
            self.identifier = model_obj.aliquot_identifier
        self.object = model_obj

        self.identifier = self.object.aliquot_identifier

    def __str__(self):
        return self.object.aliquot_identifier
