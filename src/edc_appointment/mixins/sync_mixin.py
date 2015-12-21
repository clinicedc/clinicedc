from django.db import models

try:
    from edc_sync.mixins import SyncMixin
except ImportError:
    class SyncMixin(models.Model):
        class Meta:
            abstract = True
