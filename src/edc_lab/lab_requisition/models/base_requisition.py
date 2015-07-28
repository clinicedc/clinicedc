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
        blank=True,
    )

    subject_identifier = models.CharField(
        max_length=25,
        null=True,
        editable=False
    )

    def natural_key(self):
        return (self.requisition_identifier,)

    def dashboard(self):
        url = reverse('subject_dashboard_url',
                      kwargs={'dashboard_type': self.visit.appointment.registered_subject.subject_type.lower(),
                              'dashboard_model': 'appointment',
                              'dashboard_id': self.visit.appointment.pk,
                              'show': 'appointments'})
        return """<a href="{url}" />dashboard</a>""".format(url=url)
    dashboard.allow_tags = True

    class Meta:
        abstract = True
