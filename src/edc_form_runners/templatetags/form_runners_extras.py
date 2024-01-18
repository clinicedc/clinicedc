from __future__ import annotations

from typing import TYPE_CHECKING

from django import template
from django.db import models
from edc_crf.model_mixins import CrfModelMixin

from edc_form_runners.utils import get_form_runner_issues

if TYPE_CHECKING:

    class Model(CrfModelMixin, models.Model):
        ...


register = template.Library()


@register.inclusion_tag(f"edc_form_runners/form_runner_issues.html")
def show_form_runner_issues(model_obj: Model | None):
    messages = []
    if model_obj:
        qs = get_form_runner_issues(
            model_obj._meta.label_lower,
            getattr(model_obj, model_obj.related_visit_model_attr()),
            panel_name=getattr(model_obj, "panel_name", None),
        )
        messages = [f"{obj.message} [{obj.field_name}]" for obj in qs]
    return dict(messages="<BR>".join(messages))
