from ..exceptions import RelatedVisitFieldError
from .visit_model_mixin import VisitModelMixin


def get_related_visit_model_attr(model_cls) -> str:
    """Returns the field name for the visit model foreign key
    or raises.

    Note: may also be the reverse relation. For example, if this is an
    `appointment` model class, the relation is a reverse relation where
    the attr name, given related to SubjectVisit, has a fld class
    attr in `subjectvisit` and not `subject_visit`.

    If the reverse attr is not found, check value of `related_name` in the
    field class.
    """
    attrs = []
    for fld_cls in model_cls._meta.get_fields():
        if fld_cls.related_model is not None and issubclass(
            fld_cls.related_model, (VisitModelMixin,)
        ):
            attrs.append(fld_cls.name)
            break
    if len(attrs) > 1:
        raise RelatedVisitFieldError(
            f"More than one field is related to a visit model. Got {attrs}."
        )
    elif len(attrs) == 0:
        raise RelatedVisitFieldError(
            f"{model_cls} has no related visit model. "
            f"Expected the related visit model to be an instance "
            "of `VisitModelMixin`."
        )
    return attrs[0]
