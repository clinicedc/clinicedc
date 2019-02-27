class PrimaryAliquotError(Exception):
    pass


class PrimaryAliquotPrefixError(Exception):
    pass


class PrimaryAliquot:

    """A class that gets or creates the primary aliquot.
    """

    def __init__(
        self,
        aliquot_type=None,
        subject_identifier=None,
        requisition_identifier=None,
        identifier_prefix=None,
        aliquot_creator_cls=None,
    ):
        self._object = None
        self.aliquot_creator_cls = aliquot_creator_cls
        self.aliquot_type = aliquot_type
        self.requisition_identifier = requisition_identifier
        self.subject_identifier = subject_identifier
        self.identifier_prefix = identifier_prefix
        self.subject_identifier = subject_identifier
        self.identifier = self.object.aliquot_identifier

    def __str__(self):
        return self.object.aliquot_identifier

    @property
    def object(self):
        """Returns an existing or newly created aliquot model instance.
        """
        if not self._object:
            aliquot_creator = self.aliquot_creator_cls(
                identifier_prefix=self.identifier_prefix,
                is_primary=True,
                requisition_identifier=self.requisition_identifier,
                subject_identifier=self.subject_identifier,
            )
            self._object = aliquot_creator.create_primary(
                aliquot_type=self.aliquot_type
            )
        return self._object
