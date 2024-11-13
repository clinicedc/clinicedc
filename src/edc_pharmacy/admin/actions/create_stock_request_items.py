from datetime import timezone
from typing import TYPE_CHECKING

from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext
from edc_utils import get_utcnow
from sequences import get_next_value

from ...analytics import stock_request_for_subjects_df
from ...models import StockRequestItem

if TYPE_CHECKING:
    from ...models import StockRequest


@admin.display(description="Prepare stock request items")
def create_stock_request_items_action(modeladmin, request, queryset):
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
        now = get_utcnow()
        stock_request_obj: StockRequest = queryset.first()

        # allowe delete if not yet allocated
        StockRequestItem.objects.filter(
            stock_request=stock_request_obj, allocation__isnull=True
        ).delete()

        df = stock_request_for_subjects_df(stock_request_obj)

        if stock_request_obj.subject_identifiers:
            subject_identifiers = stock_request_obj.subject_identifiers.split("\n")
            df = df[df.subject_identifier.isin(subject_identifiers)]
            df = df.reset_index(drop=True)
        elif stock_request_obj.excluded_subject_identifiers:
            excluded_subject_identifiers = (
                stock_request_obj.excluded_subject_identifiers.split("\n")
            )
            df = df[~df.subject_identifier.isin(excluded_subject_identifiers)]
            df = df.reset_index(drop=True)

        # df_in_stock = in_stock_for_subjects_df(stock_request_obj)
        # df = df.merge(
        #     df_in_stock[["in_stock", "stock_identifier"]], on="stock_identifier", how="left"
        # )
        # need to know more than just "in_stock", need to know the number in stock
        data = []
        for i, row in df.iterrows():
            for _ in range(0, stock_request_obj.containers_per_subject):
                next_id = get_next_value(StockRequestItem._meta.label_lower)
                obj = StockRequestItem(
                    stock_request=stock_request_obj,
                    request_item_identifier=f"{next_id:06d}",
                    rx_id=row["rx_id"],
                    registered_subject_id=row["registered_subject_id"],
                    visit_code=str(int(row["next_visit_code"])),
                    visit_code_sequence=int(10 * row["next_visit_code"] % 1),
                    appt_datetime=row["next_appt_datetime"].replace(tzinfo=timezone.utc),
                    # in_stock=row["in_stock"],
                    created=now,
                )
                data.append(obj)
        created = len(StockRequestItem.objects.bulk_create(data))

        # check for items in stock at site

        url = reverse("edc_pharmacy_admin:edc_pharmacy_stockrequest_changelist")
        url = f"{url}?q={stock_request_obj.request_identifier}"
        msg = format_html(
            gettext(
                "Created %(qty)s items per subject for request %(request_identifier)s "
                "with a total of %(created)s items."
            )
            % {
                "created": created,
                "request_identifier": stock_request_obj.request_identifier,
                "url": url,
                "qty": stock_request_obj.containers_per_subject,
            }
        )
        messages.add_message(request, messages.SUCCESS, message=msg)
