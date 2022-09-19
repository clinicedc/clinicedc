from ..exceptions import RelatedVisitFieldError
from .visit_model_mixin import VisitModelMixin


def get_related_visit_model_attr(model_cls) -> str:
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
