from typing import TYPE_CHECKING

from celery.states import PENDING
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext
from edc_utils.celery import get_task_result

if TYPE_CHECKING:

    from ...models import StockRequest


@admin.display(description="Prepare stock request items")
def prepare_stock_request_items_action(modeladmin, request, queryset):
    """
    1. is there an open unprocess stock request?
    2. what stock is available at the site?
    3. what stock is available at central?

    """
    if queryset.count() > 1 or queryset.count() == 0:
        messages.add_message(
            request,
            messages.ERROR,
            gettext("Select one and only one item"),
        )
    else:
        stock_request: StockRequest = queryset.first()
        if getattr(get_task_result(stock_request), "status", "") == PENDING:
            messages.add_message(
                request,
                messages.ERROR,
                (
                    f"Stock request {stock_request.request_identifier} is still processing. "
                    "Please click cancel and check the status column."
                ),
            )
        else:
            url = reverse(
                "edc_pharmacy:review_stock_request_url",
                kwargs={"stock_request": stock_request.pk},
            )
            return HttpResponseRedirect(url)
    return None
