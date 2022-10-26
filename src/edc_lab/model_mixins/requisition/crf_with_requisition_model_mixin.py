from django.db import models
from django.db.models import PROTECT
from edc_model.validators import datetime_not_future

from edc_lab import RequisitionPanel
from edc_lab.utils import get_requisition_model_name

requisition_fk_options = dict(
    to=get_requisition_model_name(),
    on_delete=PROTECT,
    related_name="+",
    verbose_name="Requisition",
    null=True,
    blank=True,
    help_text="Start typing the requisition identifier or select one from this visit",
)


class CrfWithRequisitionModelMixin(models.Model):

    """You may also wish to override field `requisition`
    to include `limit_choices_to`.

    For example:
        from edc_lab.model_mixins import (
            CrfWithRequisitionModelMixin,
            requisition_fk_options,
            )

        class MyRequisition(CrfWithRequisitionModelMixin, etc):
            ...
            lab_panel = fbc_panel
            requisition = models.ForeignKey(
                limit_choices_to={"panel__name": fbc_panel.name},
                **requisition_fk_options,
            )
            ...
    """

    lab_panel: RequisitionPanel = None

    requisition = models.ForeignKey(**requisition_fk_options)

    assay_datetime = models.DateTimeField(
        verbose_name="Result assay date and time",
        validators=[datetime_not_future],
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
