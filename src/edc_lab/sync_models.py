from edc_sync.site_sync_models import site_sync_models

site_sync_models.register_for_app('edc_lab', exclude_models=['edc_lab.panel'])
