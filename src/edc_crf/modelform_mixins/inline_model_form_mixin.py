from __future__ import annotations

from typing import TYPE_CHECKING

from edc_visit_tracking.modelform_mixins import get_related_visit

if TYPE_CHECKING:
    from edc_visit_tracking.model_mixins import VisitModelMixin


class InlineCrfModelFormMixin:
    @property
    def related_visit(self) -> VisitModelMixin:
        """Return the instance of the inline parent model's visit
        model.
        """
        return get_related_visit(
            self,
            related_visit_model_attr=self.instance.parent_model.related_visit_model_attr(),
        )

    @property
    def related_visit_model_attr(self) -> str:
        return self.instance.parent_model.related_visit_model_attr()
