from django_offline.site_offline_models import site_offline_models
from django_offline.offline_model import OfflineModel


offline_models = [
    'edc_export.objecthistory',
    'edc_export.exportplan',
    'edc_export.exportreceipt',
    'edc_export.filehistory',
    'edc_export.uploadexportreceiptfile',
]

site_offline_models.register(offline_models, OfflineModel)
