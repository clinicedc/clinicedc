from ..exceptions import RelatedVisitFieldError
from ..utils import get_related_visit_model_cls


def get_related_visit_model_attr(model_cls) -> str:
    """Returns the field name for the visit model foreign key
    or raises.

    Note: may also be the reverse relation. For example, if this is
    an `appointment` model class, the relation is a reverse relation
    where the attr name, given related to SubjectVisit, has a fld
    class attr in `subjectvisit` and not `subject_visit`.

    If the reverse attr is not found, check value of `related_name`
    in the field class, otherwise raise an exception.

    If more than one is found, raise an exception.
    """
    attrs = []
    related_visit_model_cls = get_related_visit_model_cls()
    if related_visit_model_cls._meta.proxy is True:
        related_visit_model_cls = related_visit_model_cls._meta.proxy_for_model
    for fld_cls in model_cls._meta.get_fields():
        if (
            fld_cls.related_model is not None
            and fld_cls.related_model == related_visit_model_cls
        ):
            attrs.append(fld_cls.name)  # noqa: PERF401
    if len(attrs) > 1:
        raise RelatedVisitFieldError(
            f"More than one field is related to the visit model. See {model_cls}. "
            f"Got {attrs}. "
        )
    if len(attrs) == 0:
        raise RelatedVisitFieldError(
            f"{model_cls} has no related visit model. "
            f"Expected the related visit model to be an instance "
            "of `VisitModelMixin`."
        )
    return attrs[0]
