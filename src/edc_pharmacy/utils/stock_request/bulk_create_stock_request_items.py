from __future__ import annotations

from datetime import timezone
from typing import TYPE_CHECKING

from django.apps import apps as django_apps
from edc_utils import get_utcnow
from sequences import get_next_value

if TYPE_CHECKING:
    import pandas as pd

    from ...models import StockRequest


def bulk_create_stock_request_items(stock_request: StockRequest, df: pd.DataFrame) -> int:
    stock_request_item_model_cls = django_apps.get_model("edc_pharmacy.StockRequestItem")
    registered_subject_model_cls = django_apps.get_model("edc_registration.registeredsubject")
    rx_model_cls = django_apps.get_model("edc_pharmacy.rx")
    now = get_utcnow()
    data = []
    for i, row in df[df.stock_qty == 0].iterrows():
        registered_subject = registered_subject_model_cls.objects.get(
            id=row["registered_subject_id"]
        )
        rx = rx_model_cls.objects.get(registered_subject=registered_subject)
        visit_code = str(int(row["next_visit_code"]))
        visit_code_sequence = int(10 * row["next_visit_code"] % 1)
        appt_datetime = row["next_appt_datetime"].replace(tzinfo=timezone.utc)
        assignment = rx.get_assignment()
        next_id = get_next_value(stock_request_item_model_cls._meta.label_lower)
        request_item_identifier = f"{next_id:06d}"
        obj = stock_request_item_model_cls(
            stock_request=stock_request,
            request_item_identifier=request_item_identifier,
            registered_subject=registered_subject,
            visit_code=visit_code,
            visit_code_sequence=visit_code_sequence,
            rx=rx,
            appt_datetime=appt_datetime,
            assignment=assignment,
            created=now,
        )
        data.append(obj)
    return len(stock_request_item_model_cls.objects.bulk_create(data))
