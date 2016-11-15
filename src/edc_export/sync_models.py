from edc_sync.site_sync_models import site_sync_models
from edc_sync.sync_model import SyncModel


sync_models = [
    'edc_export.exporthistory',
    'edc_export.exportplan',
    'edc_export.exportreceipt',
    'edc_export.exporttransaction',
    'edc_export.uploadexportreceiptfile',
]

site_sync_models.register(sync_models, SyncModel)
