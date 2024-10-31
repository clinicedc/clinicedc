from django.contrib.sites.models import Site
from django.db import models
from edc_constants.constants import OPEN
from edc_model.models import BaseUuidModel

from ...constants import CANCELLED
from ..medication import Formulation


class StockTransferRequest(BaseUuidModel):
    """A model that initiates a transfer of medication from one
    location to the other.

    Typically, this is a request to move medication stock from
    the central pharmacy to a site.

    A stock transfer request is initiated by the site.

    A signal will generate the items for this request which may be
    reveiwed by the site before final submission.

    Status should be UNDER REVIEW, SUBMITTED, CANCELLED

    Perhaps track the number of items after review,
    need "partialled fulfilled" status?
    """

    request_identifier = models.CharField(max_length=50, unique=True)
    request_date = models.DateField()
    site = models.ForeignKey(Site, on_delete=models.PROTECT)
    formulation = models.ForeignKey(Formulation, on_delete=models.PROTECT)
    qty = models.IntegerField(null=True, blank=True, help_text="Autofilled")
    status = models.CharField(
        max_length=25,
        choices=(
            (OPEN, OPEN),
            ("ON_ORDER", "ON_ORDER"),
            ("FULFILLED", "FULFILLED"),
            (CANCELLED, CANCELLED),
        ),
        default=OPEN,
    )
