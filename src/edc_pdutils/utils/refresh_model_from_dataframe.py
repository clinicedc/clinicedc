import pandas as pd
from django.apps import apps as django_apps
from django.db import models


def refresh_model_from_dataframe(
    df: pd.DataFrame,
    model: str | None = None,
    model_cls: type[models.Model] | None = None,
    columns: list[str] | None = None,
) -> None:
    columns = columns or list(df.columns)
    model_cls = model_cls or django_apps.get_model(model)
    model_cls.objects.all().delete()
    model_cls.objects.bulk_create(
        [model_cls(**{col: row[col] for col in columns}) for _, row in df.iterrows()]
    )
