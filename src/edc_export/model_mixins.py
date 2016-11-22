from django.db import models
from django.utils import timezone


class ExportTrackingFieldsMixin(models.Model):

    """Adds these fields to the Concrete model."""

    exported = models.BooleanField(
        default=False,
        editable=False,
        help_text="system field for export tracking. considered 'exported' if both sent and received.")

    exported_datetime = models.DateTimeField(
        null=True,
        editable=False,
        help_text="system field for export tracking.")

    export_change_type = models.CharField(
        max_length=1,
        choices=(('I', "Insert"), ('U', "Update"), ('D', "Delete"),),
        default='I',
        editable=False,
        help_text="system field for export tracking.")

    export_uuid = models.UUIDField(
        null=True,
        editable=False,
        help_text="system field for export tracking.")

    def update_export_mixin_fields(self):
        self.exported = True
        self.exported_datetime = timezone.now()
        self.save()

    class Meta:
        abstract = True


class NotificationMixin(models.Model):

    notification_plan_name = models.CharField(max_length=200)

    notification_datetime = models.DateTimeField()

    subject = models.CharField(max_length=200)

    recipient_list = models.TextField(null=True)

    cc_list = models.TextField(null=True)

    body = models.TextField(null=True)

    status = models.CharField(
        max_length=15,
        default='new',
        choices=(
            ('new', 'New'),
            ('sent', 'Sent'),
            ('cancelled', 'Cancelled')))

    sent = models.BooleanField(default=False)

    sent_datetime = models.DateTimeField(null=True)

    class Meta:
        abstract = True
        ordering = ('notification_datetime', )


class NotificationPlanMixin(models.Model):

    name = models.CharField(max_length=50, unique=True)

    friendly_name = models.CharField(max_length=50)

    subject_format = models.TextField()

    body_format = models.TextField()

    recipient_list = models.TextField()

    cc_list = models.TextField()

    class Meta:
        app_label = 'edc_export'
