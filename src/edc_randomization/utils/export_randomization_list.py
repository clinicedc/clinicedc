from django.conf import settings
from edc_pdutils.model_to_dataframe import ModelToDataframe


def export_randomization_list(model=None, path=None):
    model = model or "edc_randomization.randomizationlist"
    df = ModelToDataframe(model=model, decrypt=True, drop_sys_columns=True)
    path = path or settings.EXPORT_FOLDER
    opts = dict(path_or_buf=path, encoding="utf-8", index=0, sep="|",)
    df.dataframe.to_csv(**opts)
