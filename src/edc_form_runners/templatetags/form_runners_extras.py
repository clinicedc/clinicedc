from __future__ import annotations

from typing import TYPE_CHECKING

from django import template

from edc_form_runners.utils import get_form_runner_issues

if TYPE_CHECKING:
    from django.db import models

    from edc_crf.model_mixins import CrfModelMixin
    from edc_metadata.models import CrfMetadata, RequisitionMetadata

    class Model(CrfModelMixin, models.Model): ...


register = template.Library()


@register.inclusion_tag("edc_form_runners/form_runner_issues.html")
def show_form_runner_issues(metadata_model_obj: CrfMetadata | RequisitionMetadata):
    messages = []
    if metadata_model_obj and metadata_model_obj.model_instance:
        model_obj = metadata_model_obj.model_instance
        related_visit = getattr(model_obj, model_obj.related_visit_model_attr())
        panel_name = getattr(metadata_model_obj, "panel_name", None)
        qs = get_form_runner_issues(
            model_obj._meta.label_lower, related_visit, panel_name=panel_name
        )
        messages = [f"{issue.message} [{issue.field_name}]" for issue in qs]
    return dict(form_runner_issues="<BR>".join(messages))
