from typing import Any, Optional

from django import forms


def get_subject_visit(modelform: Any, visit_model_attr: Optional[str]):
    if visit_model_attr not in modelform.cleaned_data:
        subject_visit = getattr(modelform.instance, visit_model_attr, None)
        if not subject_visit:
            raise forms.ValidationError(f"Field `{visit_model_attr}` is required (2).")
    else:
        subject_visit = modelform.cleaned_data.get(visit_model_attr)
    return subject_visit
