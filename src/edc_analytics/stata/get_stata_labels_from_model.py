import re

import pandas as pd
from bs4 import BeautifulSoup
from django.apps import apps as django_apps


def strip_html(text: str) -> str:
    if pd.isna(text):
        return text
    if bool(re.search(r"<[^>]+>", text)):
        return BeautifulSoup(text, "html.parser").get_text()
    return text


# def get_stata_labels_from_model(df: pd.DataFrame, model: str, suffix: str) -> dict[str:str]:
#     """Generate STATA labels"""
#     labels = {}
#     _, model_name = model.split(".")
#     model_cls = django_apps.get_model(model)
#     for fld in model_cls._meta.get_fields():
#         if f"{fld.name}_{suffix}" in df.columns:
#             labels.update({f"{fld.name}_{suffix}": strip_html(str(fld.verbose_name)[:80])})
#     return labels


def get_stata_labels_from_model(
    df: pd.DataFrame, model: str, suffix: str | None = None
) -> dict[str:str]:
    """Generate STATA labels"""
    labels = {}
    _, model_name = model.split(".")
    model_cls = django_apps.get_model(model)
    for fld in model_cls._meta.get_fields():
        if suffix:
            if f"{fld.name}_{suffix}" in df.columns:
                labels.update({f"{fld.name}_{suffix}": strip_html(str(fld.verbose_name)[:80])})
        elif f"{fld.name}_{suffix}" in df.columns:
            try:
                labels.update({fld.name: strip_html(str(fld.verbose_name)[:80])})
            except AttributeError:
                pass
    return labels
