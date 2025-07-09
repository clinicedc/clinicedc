from __future__ import annotations

from datetime import timezone
from typing import TYPE_CHECKING

import pandas as pd
from celery import shared_task
from django.apps import apps as django_apps
from edc_utils import get_utcnow
from sequences import get_next_value

if TYPE_CHECKING:
    from uuid import UUID


@shared_task
def bulk_create_stock_request_items(
    stock_request_pk: UUID,
    nostock_as_dict: dict,
    user_created: str | None = None,
    bulk_create: bool | None = None,
) -> None:
    bulk_create = True if bulk_create is None else bulk_create
    stock_request_model_cls = django_apps.get_model("edc_pharmacy.StockRequest")
    stock_request_item_model_cls = django_apps.get_model("edc_pharmacy.StockRequestItem")
    registered_subject_model_cls = django_apps.get_model("edc_registration.registeredsubject")
    rx_model_cls = django_apps.get_model("edc_pharmacy.rx")

    stock_request = stock_request_model_cls.objects.get(pk=stock_request_pk)
    df_nostock = pd.DataFrame(nostock_as_dict)
    now = get_utcnow()
    data = []
    for i, row in df_nostock[df_nostock.stock_qty == 0].iterrows():
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
            user_created=user_created,
            created=now,
        )
        data.append(obj)
    if data:
        if bulk_create:
            stock_request_item_model_cls.objects.bulk_create(data)
        else:
            for obj in data:
                obj.save()
        stock_request.item_count = len(data)
        stock_request.save(update_fields=["item_count"])
    return None


__all__ = ["bulk_create_stock_request_items"]
