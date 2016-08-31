from datetime import datetime
from collections import namedtuple

from django.db import models


DestinationTuple = namedtuple('DestinationTuple', 'code name address tel email')


class PackingListModelMixin(models.Model):

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

    received = models.BooleanField(
        default=False,
        help_text='Shipped items are all received at destination',
        editable=False)

    def save(self, *args, **kwargs):
        if not self.list_datetime:
            self.list_datetime = datetime.now()
        if not self.timestamp:
            self.timestamp = datetime.today().strftime('%Y%m%d%H%M%S%f')
        super(PackingListModelMixin, self).save(*args, **kwargs)

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

    class Meta:
        abstract = True
        ordering = ['list_datetime', ]


class PackingListItemModelMixin(models.Model):

    requisition = models.CharField(
        max_length=36,
        null=True,
        blank=False,
        editable=False,
        help_text="pk of requisition instance")

    item_reference = models.CharField(
        max_length=25)

    item_datetime = models.DateTimeField(
        null=True,
        blank=True)

    item_description = models.TextField(
        max_length=100,
        null=True,
        blank=True)

    item_priority = models.CharField(
        max_length=35,
        choices=(('normal', 'Normal'), ('urgent', 'Urgent')),
        null=True,
        blank=False,
        help_text="")

    old_panel_id = models.CharField(max_length=50, null=True)

    received = models.BooleanField(
        default=False,
        help_text='Shipped items are all received at destination',
        editable=False)

    received_datetime = models.DateTimeField(
        null=True,
        help_text='Date and time shipped item was received at destination',
        editable=False)

    def __str__(self):
        return '{} {}'.format(self.item_reference, self.item_datetime.strftime('%Y-%m-%d'))

    def packing_list_model(self):
        for field in self._meta.fields:
            try:
                if issubclass(field.rel.to, PackingListMixin):
                    return (field.attname, field.rel.to)
            except:
                pass
        return (None, None)

    def view_packing_list(self):
        packing_list_field_attname, packing_list_model = self.packing_list_model()
        if packing_list_model:
            return '<a href="/admin/{app_label}/{object_name}/?q={pk}">{timestamp}</a>'.format(
                app_label=packing_list_model._meta.app_label,
                object_name=packing_list_model._meta.object_name.lower(),
                timestamp=packing_list_model.objects.get(
                    pk=getattr(self, packing_list_field_attname)).timestamp,
                pk=getattr(self, packing_list_field_attname),
            )
        else:
            return 'packing list'
    view_packing_list.allow_tags = True

    def priority(self):
        style = ''
        priority = ''
        if self.item_priority:
            priority = self.item_priority.lower()
            if priority == 'urgent':
                style = 'color:red;font-weight:700'
            if priority == 'normal':
                priority = ''
        return '<span style="{style}">{priority}</span>'.format(style=style, priority=priority)
    priority.allow_tags = True

    def specimen(self):
        return '{item_reference}<BR>{requisition}</a>'.format(item_reference=self.item_reference,
                                                              requisition=self.requisition.replace('requisition', ''))
    specimen.allow_tags = True

    def description(self):
        return self.item_description.replace(' ', '<BR>')
    description.allow_tags = True

    def get_subject_identifier(self):
        return ''

    class Meta:
        abstract = True
        ordering = ['created', ]


class DestinationModelMixin(models.Model):

    code = models.CharField(
        verbose_name='Code',
        max_length=25,
        unique=True)

    name = models.CharField(
        verbose_name='Name',
        max_length=50,
        unique=True)

    address = models.TextField(
        verbose_name='Address',
        max_length=250)

    tel = models.CharField(
        verbose_name='Telephone',
        max_length=50)

    email = models.CharField(
        verbose_name='Email',
        max_length=25)

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.code, )

    def is_serialized(self):
        return False

    class Meta:
        abstract = True
        unique_together = (('code', 'name'), )
