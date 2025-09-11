from __future__ import annotations

from decimal import Decimal

import pandas as pd
from django.apps import apps as django_apps
from django.contrib.sites.models import Site
from django.db.models import DecimalField, ExpressionWrapper, F
from django_pandas.io import read_frame


def in_stock_for_subjects_df(
    container_name: str = None, product_name: str = None
) -> pd.DataFrame:
    """Returns a dataframe of stock allocated to a subject_identifier.

    Filter by site_id to keep those rows already at a study site.

        df_subject_stock = df_subject_stock[
            df_subject_stock.site_id.notna()
        ]


    """
    location_cls = django_apps.get_model("edc_pharmacy.location")
    stock_cls = django_apps.get_model("edc_pharmacy.stock")

    # qs of stock in stock and allocated to a subject_identifier
    difference = ExpressionWrapper(F("qty_in") - F("qty_out"), output_field=DecimalField())
    qs = (
        stock_cls.objects.filter(
            allocation__isnull=False,
            confirmation__isnull=False,
            stocktransferitem__isnull=False,
            confirmationatsiteitem__isnull=False,
            container__name=container_name,
            dispenseitem__isnull=True,
            product__name__icontains=product_name,
        )
        .values(
            "stock_identifier",
            "code",
            "allocation__registered_subject__subject_identifier",
            "qty_in",
            "qty_out",
            "container__name",
            "location",
            "product",
        )
        .annotate(container_qty=difference)
        .filter(qty__gte=Decimal("1.00"))
    )

    # read df
    df = read_frame(qs, verbose=False).rename(
        columns={
            "allocation__registered_subject__subject_identifier": "subject_identifier",
            "container__name": "container",
        }
    )
    df["in_stock"] = True

    # merge in site_id
    df_sites = read_frame(Site.objects.all(), verbose=False)
    df_sites = df_sites.rename(columns={"id": "site_id"})
    df_location = read_frame(location_cls.objects.all(), verbose=False)
    df_location = df_location.merge(df_sites[["name", "site_id"]], on="name", how="left")
    df_location = df_location.rename(columns={"id": "location"})
    df = df.merge(df_location[["location", "site_id"]], how="left", on="location")

    # sort
    df = df.sort_values(by=["subject_identifier", "stock_identifier"])
    df = df.reset_index(drop=True)
    return df
