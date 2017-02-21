from edc_sync.site_sync_models import site_sync_models
from edc_sync.sync_model import SyncModel


sync_models = [
    'edc_lab.aliquot',
    'edc_lab.box',
    'edc_lab.boxitem',
    'edc_lab.boxtype',
    'edc_lab.destination',
    'edc_lab.manifest',
]

site_sync_models.register(sync_models, SyncModel)
