from django.core.urlresolvers import reverse
from django.db import models

from edc_base.model.constants import BASE_MODEL_UPDATE_FIELDS, BASE_UUID_MODEL_UPDATE_FIELDS
from edc_lab.lab_clinic_api.models import TestCode

from .base_base_requisition import BaseBaseRequisition


class BaseRequisition (BaseBaseRequisition):

    # populate this one based on the selected panel at the dashboard
    test_code = models.ManyToManyField(
        TestCode,
        verbose_name='Additional tests',
        null=True,
        blank=True)

    subject_identifier = models.CharField(
        max_length=25,
        null=True,
        editable=False)

    def save(self, *args, **kwargs):
        self.subject_identifier = self.get_visit().get_subject_identifier()
        super(BaseRequisition, self).save(*args, **kwargs)

    def dispatch_container_lookup(self, using=None):
        return None

    def bypass_for_edit_dispatched_as_item(self, using=None, update_fields=None):
        """Allow bypass only if doing lab actions."""
        # requery myself
        obj = self.__class__.objects.using(using).get(pk=self.pk)
        # dont allow values in these fields to change if dispatched
        may_not_change_these_fields = [(k, v) for k, v in obj.__dict__.iteritems() if k not in [
            'is_receive', 'is_receive_datetime', 'is_labelled', 'is_labelled_datetime', 'protocol',
            'specimen_identifier', 'is_packed', 'packing_list_id', 'is_lis'] +
            BASE_MODEL_UPDATE_FIELDS + BASE_UUID_MODEL_UPDATE_FIELDS]
        for k, v in may_not_change_these_fields:
            if k[0] != '_':
                if getattr(self, k) != v:
                    return False
        return True

    def natural_key(self):
        return (self.requisition_identifier,)

    def get_subject_identifier(self):
        return self.get_visit().subject_identifier

    def get_visit(self):
        raise TypeError('method \'get_visit()\' in BaseRequisition must be overidden')

    def dashboard(self):
        url = reverse('subject_dashboard_url',
                      kwargs={'dashboard_type': self.get_visit().appointment.registered_subject.subject_type.lower(),
                              'dashboard_model': 'appointment',
                              'dashboard_id': self.get_visit().appointment.pk,
                              'show': 'appointments'})
        return """<a href="{url}" />dashboard</a>""".format(url=url)
    dashboard.allow_tags = True

    class Meta:
        abstract = True
