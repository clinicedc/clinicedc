from django.apps import apps as django_apps
from django.db import models

from .packing_list_mixin import PackingListMixin


class BasePackingListItem(models.Model):

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

    def __unicode__(self):
        return '{} {}'.format(self.item_reference, self.item_datetime.strftime('%Y-%m-%d'))

    def gender(self):
        """Users may override."""
        return None

    def clinician(self):
        """Users may override."""
        # TODO: doesn't work
        retval = "n/a"
        try:
            Requisition = django_apps.get_model(self._meta.app_label, self.requisition)
        except:
            Requisition = None
            retval = '?'
        if self.item_reference and Requisition:
            requisition = Requisition.objects.get(specimen_identifier=self.item_reference)
            retval = requisition.user_created
        return retval

    def drawn_datetime(self):
        # TODO: doesn't work
        retval = "n/a"
        try:
            Requisition = django_apps.get_model(self._meta.app_label, self.requisition)
        except:
            Requisition = None
            retval = '?'
        if self.item_reference and Requisition:
            requisition = Requisition.objects.get(specimen_identifier=self.item_reference)
            retval = requisition.drawn_datetime.strftime('%Y-%m-%d %H:%M')
        return retval

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
