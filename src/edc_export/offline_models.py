from django_collect_offline.offline_model import OfflineModel
from django_collect_offline.site_offline_models import site_offline_models

offline_models = [
    "edc_export.objecthistory",
    "edc_export.exportplan",
    "edc_export.exportreceipt",
    "edc_export.filehistory",
    "edc_export.uploadexportreceiptfile",
]

site_offline_models.register(offline_models, OfflineModel)
