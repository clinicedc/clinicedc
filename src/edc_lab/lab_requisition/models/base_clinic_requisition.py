from django.db import models

from ..models import BaseRequisition


class BaseClinicRequisition (BaseRequisition):

    dmis_identifier = models.CharField(max_length=25, null=True, editable=False)

    old_panel_id = models.CharField(max_length=50, null=True, editable=False)

    old_aliquot_type_id = models.CharField(max_length=50, null=True, editable=False)

    def bypass_for_edit_dispatched_as_item(self, using=None, update_fields=None):
        # requery myself
        obj = self.__class__.objects.get(pk=self.pk)
        # dont allow values in these fields to change if dispatched
        may_not_change_these_fields = [(k, v) for k, v in obj.__dict__.iteritems() if k not in [
            'is_receive', 'is_receive_datetime', 'specimen_identifier', 'is_packed', 'is_labelled',
            'is_labelled_datetime', 'is_lis', 'packing_list', 'comment', 'modified', 'user_modified']
        ]
        for k, v in may_not_change_these_fields:
            if k[0] != '_':
                if getattr(self, k) != v:
                    return False
        return True

    class Meta:
        abstract = True
