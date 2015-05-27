from django.db import models
from django.core.serializers.base import SerializationError
from edc.subject.visit_tracking.models import BaseVisitTracking
from ..models import BaseRequisition


class BaseClinicRequisition (BaseRequisition):

    dmis_identifier = models.CharField(max_length=25, null=True, editable=False)

    old_panel_id = models.CharField(max_length=50, null=True, editable=False)

    old_aliquot_type_id = models.CharField(max_length=50, null=True, editable=False)

    def get_visit(self):
        for field in self._meta.fields:
            try:
                if issubclass(field.rel.to, BaseVisitTracking):
                    return field.rel.to.objects.get(pk=getattr(self, field.attname))
            except:
                pass
        raise TypeError('{0} is unable to determine the visit model'.format(self))
        return None

    def get_subject_identifier(self):
        return self.get_visit().appointment.registered_subject.subject_identifier

    def natural_key(self):
        raise SerializationError('Requisition subclass must override method \'natural key\'.')

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
