from datetime import datetime

from django.db import models

from simple_history.models import HistoricalRecords as AuditTrail

from .destination import Destination


class PackingListMixin(models.Model):

    list_datetime = models.DateTimeField()

    list_comment = models.CharField(
        verbose_name='Instructions',
        max_length=100,
        null=True,
        blank=True)

    list_items = models.TextField(
        max_length=1000,
        help_text='List specimen_identifier\'s. One per line.')

    timestamp = models.CharField(
        max_length=35,
        null=True)

    destination = models.ForeignKey(
        Destination,
        verbose_name='Ship Specimens To',
        null=True)

    received = models.BooleanField(
        default=False,
        help_text='Shipped items are all received at destination',
        editable=False)

    history = AuditTrail()

    def save(self, *args, **kwargs):
        if not self.list_datetime:
            self.list_datetime = datetime.now()
        if not self.timestamp:
            self.timestamp = datetime.today().strftime('%Y%m%d%H%M%S%f')
        super(PackingListMixin, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.timestamp

    def reference(self):
        return self.timestamp

    def natural_key(self):
        return self.timestamp

    def specimen_count(self):
        lst = filter(None, self.list_items.replace('\r', '').split('\n'))
        return len(lst)

    def view_list_items(self):
        return '<a href="/admin/{app_label}/{object_name}item/?q={pk}">{count} items</a>'.format(
            app_label=self._meta.app_label,
            object_name=self._meta.object_name.lower(),
            pk=self.id,
            count=self.specimen_count())
    view_list_items.allow_tags = True

#     def get_subject_identifier(self):
#         return ''

    class Meta:
        abstract = True
        ordering = ['list_datetime', ]
