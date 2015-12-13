from django.db import models

from edc_base.model.models import BaseUuidModel


class ExportPlan(BaseUuidModel):

    app_label = models.CharField(max_length=50)

    object_name = models.CharField(max_length=50)

    fields = models.TextField(max_length=500)

    extra_fields = models.TextField(max_length=500)

    exclude = models.TextField(max_length=500)

    header = models.BooleanField(default=True)

    track_history = models.BooleanField(default=True)

    show_all_fields = models.BooleanField(default=True)

    delimiter = models.CharField(max_length=1, default=',')

    encrypt = models.BooleanField(default=False)

    strip = models.BooleanField(default=True)

    target_path = models.CharField(max_length=250, default='~/export')

    notification_plan_name = models.CharField(max_length=50, null=True)

    def __unicode__(self):
        return '{}.{}'.format(self.app_label, self.object_name)

    def is_serialized(self, serialize=True):
        return False

    class Meta:
        app_label = 'export'
        unique_together = (('app_label', 'object_name'), )
