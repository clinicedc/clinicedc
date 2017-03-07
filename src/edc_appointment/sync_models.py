from edc_sync.site_sync_models import site_sync_models
from edc_sync.sync_model import SyncModel

sync_models = [
    'edc_appointment.holiday']

site_sync_models.register(sync_models, SyncModel)
