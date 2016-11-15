from edc_sync.site_sync_models import site_sync_models
from edc_sync.sync_model import SyncModel


sync_models = [
    'edc_identifier.IdentifierTracker',
    'edc_identifier.SubjectIdentifier'
]

site_sync_models.register(sync_models, SyncModel)
