from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
from django.db.models import Q
from django_pandas.io import read_frame

from edc_appointment.analytics import get_appointment_df
from edc_appointment.constants import NEW_APPT
from edc_registration import get_registered_subject_model_cls
from edc_sites.site import sites as site_sites

from ...models import Rx

if TYPE_CHECKING:
    from ...models import StockRequest


def get_next_scheduled_visit_for_subjects_df(
    stock_request: StockRequest | None = None,
) -> pd.DataFrame:
    # get the next scheduled visit from appointment
    # subject_identifier, next_visit_code, next_appt_datetime
    df_appt = get_appointment_df(
        normalize=True,
        localize=True,
        values=[
            "id",
            "subject_identifier",
            "visit_code",
            "visit_code_sequence",
            "site",
            "appt_datetime",
            "appt_status",
            "appt_type",
        ],
        site_id=int(stock_request.location.site_id) if stock_request else None,
    )
    if df_appt.empty:
        df = pd.DataFrame()
    else:
        if stock_request:
            if stock_request.start_datetime:
                df_appt = df_appt[
                    df_appt.next_appt_datetime
                    >= pd.Timestamp(stock_request.start_datetime.date()).to_datetime64()
                ]
                df_appt = df_appt.reset_index(drop=True)
            if stock_request.cutoff_datetime:
                df_appt = df_appt[
                    df_appt.next_appt_datetime
                    <= pd.Timestamp(stock_request.cutoff_datetime.date()).to_datetime64()
                ]
                df_appt = df_appt.reset_index(drop=True)
        # get the first appointment due
        df = (
            df_appt[(df_appt.appt_status == NEW_APPT) & (df_appt.visit_code_sequence == 0)]
            .sort_values(by=["appt_datetime"])
            .groupby(by=["subject_identifier"])
            .first()
        )
        df = df.reset_index()
        df = df.sort_values(by=["next_appt_datetime"])
        df = df.reset_index(drop=True)

        # merge with registered_subject
        df_registered_subject = read_frame(
            get_registered_subject_model_cls().objects.values("id", "subject_identifier"),
            verbose=False,
        )
        df_registered_subject = df_registered_subject.rename(
            columns={"id": "registered_subject_id"}
        )
        df = df.merge(
            df_registered_subject,
            on="subject_identifier",
            how="left",
            suffixes=("", "_y"),
        )
        df = df.reset_index(drop=True)

        if stock_request:
            # merge with prescription
            df_rx = read_frame(
                Rx.objects.values(
                    "id",
                    "registered_subject__subject_identifier",
                    "rx_expiration_date",
                    "rando_sid",
                ).filter(
                    (
                        Q(rx_expiration_date__gte=stock_request.request_datetime.date())
                        | Q(rx_expiration_date__isnull=True)
                    ),
                    medications__in=[stock_request.formulation.medication],
                )
            )

            df_rx = df_rx.rename(
                columns={
                    "registered_subject__subject_identifier": "subject_identifier",
                    "id": "rx_id",
                }
            )
            df = df.merge(
                df_rx[["subject_identifier", "rx_id", "rando_sid"]],
                on="subject_identifier",
                how="left",
                suffixes=("", "_y"),
            )
            df = df[df.rx_id.notna()]
            df = df.reset_index(drop=True)

            df["site_name"] = df["site_id"].apply(lambda x: site_sites.get(x).name)

            if stock_request.subject_identifiers:
                subject_identifiers = stock_request.subject_identifiers.split("\n")
                df = df[df.subject_identifier.isin(subject_identifiers)]
                df = df.reset_index(drop=True)
            elif stock_request.excluded_subject_identifiers:
                excluded_subject_identifiers = (
                    stock_request.excluded_subject_identifiers.split("\n")
                )
                excluded_subject_identifiers = [
                    s.strip() for s in excluded_subject_identifiers
                ]
                df = df[~df.subject_identifier.isin(excluded_subject_identifiers)]
                df = df.reset_index(drop=True)
    return df
