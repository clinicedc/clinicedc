
class AliquotCreatorError(Exception):
    pass


class AliquotCreator:

    """A class that creates an aliquot.

    Aliquot is either a primary aliquot (is_primary=True) or
    a child aliquot (is_primary=False).
    """

    def __init__(self, parent_identifier=None, is_primary=None, aliquot_identifier_cls=None,
                 count_padding=None, identifier_length=None, parent_segment=None,
                 aliquot_model=None, identifier_prefix=None, requisition_identifier=None,
                 subject_identifier=None, **kwargs):

        self.aliquot_identifier_cls = aliquot_identifier_cls
        self.aliquot_model = aliquot_model

        self.parent_identifier = parent_identifier,
        self.is_primary = True if is_primary else False
        if not self.is_primary and not parent_identifier:
            raise AliquotCreatorError(
                'Cannot create child aliquot without parent aliquot identifier. '
                f'Got is_primary={is_primary}.')

        if not self.is_primary and not parent_segment:
            parent_segment = parent_identifier[-4:]

        self.identifier_defaults = dict(
            count_padding=count_padding,
            identifier_length=identifier_length,
            identifier_prefix=identifier_prefix,
            parent_segment=parent_segment,
        )
        self.model_defaults = dict(
            identifier_prefix=identifier_prefix,
            is_primary=self.is_primary,
            requisition_identifier=requisition_identifier,
            subject_identifier=subject_identifier,
        )

    def create(self, count=None, aliquot_type=None):
        """Returns a created aliquot model instance.
        """
        count = 1 if self.is_primary else count
        aliquot_identifier_obj = self.aliquot_identifier_cls(
            count=count,
            numeric_code=aliquot_type.numeric_code,
            **self.identifier_defaults,
        )
        parent_identifier = (
            aliquot_identifier_obj.identifier if self.is_primary else self.parent_identifier)
        aliquot = self.aliquot_model.objects.create(
            aliquot_identifier=aliquot_identifier_obj.identifier,
            aliquot_type=aliquot_type.name,
            alpha_code=aliquot_type.alpha_code,
            count=count,
            numeric_code=aliquot_type.numeric_code,
            parent_identifier=parent_identifier,
            ** self.model_defaults,
        )
        return aliquot
