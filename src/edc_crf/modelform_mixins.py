from __future__ import annotations

from typing import TYPE_CHECKING

from edc_consent.modelform_mixins import RequiresConsentModelFormMixin
from edc_form_validators import FormValidatorMixin
from edc_model_form.mixins import BaseModelFormMixin
from edc_offstudy.modelform_mixins import OffstudyCrfModelFormMixin
from edc_sites.forms import SiteModelFormMixin
from edc_visit_schedule.modelform_mixins import VisitScheduleCrfModelFormMixin
from edc_visit_tracking.modelform_mixins import (
    VisitTrackingCrfModelFormMixin,
    get_related_visit,
)

if TYPE_CHECKING:
    from edc_visit_tracking.model_mixins import VisitModelMixin


class CrfModelFormMixin(
    SiteModelFormMixin,
    RequiresConsentModelFormMixin,
    VisitScheduleCrfModelFormMixin,
    VisitTrackingCrfModelFormMixin,
    OffstudyCrfModelFormMixin,
    BaseModelFormMixin,
    FormValidatorMixin,
):
    """A modelform mixin for all CRFs.

    * Checks for the consent relative to report datetime
      and this schedule;
    * is participant on/off schedule relative to report
      datetime and this schedule;
    * validates subject_visit report datetime;
    * is participant offstudy relative to report datetime.
    """

    report_datetime_field_attr = "report_datetime"


class RequisitionModelFormMixin(CrfModelFormMixin):

    report_datetime_field_attr = "requisition_datetime"


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
