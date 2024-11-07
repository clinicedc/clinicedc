from typing import TYPE_CHECKING

import pandas as pd
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext as _
from django_pandas.io import read_frame
from edc_consent.utils import get_consent_model_cls
from edc_pdutils.dataframes import get_subject_visit
from edc_randomization.site_randomizers import site_randomizers
from edc_sites.site import sites as site_sites
from edc_utils import get_utcnow
from edc_visit_tracking.utils import get_related_visit_model
from sequences import get_next_value

from ...models import Rx, StockRequestItem
from ...utils import generate_code_with_checksum_from_id

if TYPE_CHECKING:
    from ...models import StockRequest


def create_request_items_action(modeladmin, request, queryset):
    if queryset.count() > 1 or queryset.count() == 0:
        messages.add_message(
            request,
            messages.ERROR,
            _("Select one and only one existing label specification"),
        )
    else:
        stock_request_obj: StockRequest = queryset.first()
        now = get_utcnow()
        df = get_subject_visit(model=get_related_visit_model())
        df["last_visit_datetime"] = df["last_visit_datetime"].dt.normalize()
        df = df[
            (df.visit_code == df.last_visit_code)
            & (df.visit_code_sequence == 0)
            & (df.last_visit_datetime <= pd.to_datetime("today"))
            & (df.site_id == stock_request_obj.site_id)
        ]
        df = df.reset_index(drop=True)
        df_consent = read_frame(
            get_consent_model_cls()
            .objects.values("subject_identifier", "gender")
            .filter(site=stock_request_obj.site),
            verbose=False,
        )
        df = df.merge(
            df_consent[["subject_identifier", "gender"]], on="subject_identifier", how="left"
        )
        df = df.reset_index(drop=True)
        df_rx = read_frame(
            Rx.objects.values(
                "id", "registered_subject__subject_identifier", "rx_expiration_date"
            ).filter(
                Q(rx_expiration_date__gte=get_utcnow().date())
                | Q(rx_expiration_date__isnull=True)
            )
        )

        df_rx = df_rx.rename(
            columns={
                "registered_subject__subject_identifier": "subject_identifier",
                "id": "rx_id",
            }
        )
        df = df.merge(
            df_rx[["subject_identifier", "rx_id"]], on="subject_identifier", how="left"
        )
        df = df[df.rx_id.notna()]
        df = df.reset_index(drop=True)

        df["site_name"] = df["site_id"].apply(lambda x: site_sites.get(x).name)

        data = []
        for i, row in df.iterrows():
            rx = Rx.objects.get(id=row["rx_id"])
            randomizer = site_randomizers.get(rx.randomizer_name)
            rando_obj = randomizer.model_cls().objects.get(
                subject_identifier=row["subject_identifier"]
            )
            next_id = get_next_value(StockRequestItem._meta.label_lower)
            obj = StockRequestItem(
                stock_request=stock_request_obj,
                request_item_identifier=f"{next_id:06d}",
                code=generate_code_with_checksum_from_id(next_id),
                subject_identifier=row["subject_identifier"],
                gender=row["gender"],
                site_id=row["site_id"],
                rx_id=row["rx_id"],
                sid=rando_obj.sid,
                created=now,
            )
            data.append(obj)
        created = len(StockRequestItem.objects.bulk_create(data))
        url = reverse("edc_pharmacy_admin:edc_pharmacy_stockrequest_changelist")
        url = f"{url}?q={stock_request_obj.request_identifier}"
        msg = format_html(
            _("Created request %(request_identifier)s with %(created)s records")
            % {
                "created": created,
                "request_identifier": stock_request_obj.request_identifier,
                "url": url,
            }
        )
        messages.add_message(request, messages.SUCCESS, message=msg)
