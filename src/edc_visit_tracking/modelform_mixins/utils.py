from __future__ import annotations

from typing import Any

from django import forms


def get_subject_visit(modelform: Any, related_visit_model_attr: str):
    if related_visit_model_attr not in modelform.cleaned_data:
        subject_visit = getattr(modelform.instance, related_visit_model_attr, None)
        if not subject_visit:
            raise forms.ValidationError(f"Field `{related_visit_model_attr}` is required (2).")
    else:
        subject_visit = modelform.cleaned_data.get(related_visit_model_attr)
    return subject_visit
