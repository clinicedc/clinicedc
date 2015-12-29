from django.db import models

from edc_base.audit_trail import AuditTrail
from edc_lab.lab_clinic_api.models import TestCode

from lis.core.lab_reference.models import BaseReferenceListItem

from .reference_range_list import ReferenceRangeList


class ReferenceRangeListItem(BaseReferenceListItem):

    test_code = models.ForeignKey(TestCode)

    reference_range_list = models.ForeignKey(ReferenceRangeList)

    objects = models.Manager()

    history = AuditTrail()

    def describe(self, age_in_days=None):
        if not age_in_days:
            age_in_days = 'AGE'
        if self.scale == 'increasing':
            template = ('{gender} HIV-{hiv_status} VAL{value_high_quantifier}{value_high} and '
                        'VAL{value_low_quantifier}{value_low} for {age_in_days}{age_low_quantifier}{age_low_days}d and '
                        '{age_in_days}{age_high_quantifier}{age_high_days}d')
        else:
            template = ('{gender} HIV-{hiv_status} VAL{value_low_quantifier}{value_low} and '
                        'VAL{value_high_quantifier}{value_high} for {age_in_days}{age_low_quantifier}{age_low_days}d and '
                        '{age_in_days}{age_high_quantifier}{age_high_days}d')
        return template.format(
            gender=self.gender,
            hiv_status=self.hiv_status,
            value_low_quantifier=self.value_low_quantifier,
            value_high_quantifier=self.value_high_quantifier,
            value_low=self.round_off(self.value_low),
            value_high=self.round_off(self.value_high),
            age_in_days=age_in_days,
            age_low_quantifier=self.age_low_quantifier,
            age_low_days=self.age_low_days(),
            age_high_quantifier=self.age_high_quantifier,
            age_high_days=self.age_high_days())

    def __unicode__(self):
        return "{0}".format(self.test_code.code)

    class Meta:
        app_label = 'lab_clinic_reference'
        ordering = ['test_code', 'age_low', 'age_low_unit']
