from django.db import models
from lis.core.lab_reference.models import BaseReferenceListItem
from edc_base.audit_trail import AuditTrail
from edc_constants.choices import YES_NO_NA
from edc_lab.lab_clinic_api.models import TestCode
from .grading_list import GradingList


class GradingListItem(BaseReferenceListItem):

    test_code = models.ForeignKey(TestCode)

    grading_list = models.ForeignKey(GradingList)

    grade = models.IntegerField()

    value_low_calc = models.CharField(verbose_name='Lower value is', max_length=10, choices=(('ABSOLUTE', 'Absolute'), ('LLN', 'LLN'), ('ULN', 'ULN')), default='ABSOLUTE')

    value_high_calc = models.CharField(verbose_name='Upper value is', max_length=10, choices=(('ABSOLUTE', 'Absolute'), ('LLN', 'LLN'), ('ULN', 'ULN')), default='ABSOLUTE')

    use_uln = models.BooleanField(default=False, help_text="lower/upper is X ULN")

    use_lln = models.BooleanField(default=False, help_text="lower/upper is X LLN")

    fasting = models.CharField(max_length=10, choices=YES_NO_NA, default='N/A')

    serum = models.CharField(max_length=10, choices=(('HIGH', 'High'), ('LOW', 'Low'), ('N/A', 'Not applicable')), default='N/A')

    history = AuditTrail()

    objects = models.Manager()

    def describe(self, age_in_days=None):
        if not age_in_days:
            age_in_days = 'AGE'
        if self.scale == 'decreasing':
            template = ('G{grade} {gender} HIV-{hiv_status} VAL{value_high_quantifier}{value_high}{lln}{uln} and '
                        'VAL{value_low_quantifier}{value_low}{lln}{uln} for {age_in_days}{age_low_quantifier}{age_low_days}d '
                        'and {age_in_days}{age_high_quantifier}{age_high_days}d {fasting} {serum} {comment} {dummy}')
        else:
            template = ('G{grade} {gender} HIV-{hiv_status} VAL{value_low_quantifier}{value_low}{lln}{uln} and '
                        'VAL{value_high_quantifier}{value_high}{lln}{uln} for {age_in_days}{age_low_quantifier}{age_low_days}d '
                        'and {age_in_days}{age_high_quantifier}{age_high_days}d {fasting} {serum} {comment} {dummy}')
        return template.format(
            grade=self.grade,
            gender=self.gender,
            hiv_status=self.hiv_status,
            value_low_quantifier=self.value_low_quantifier,
            value_high_quantifier=self.value_high_quantifier,
            value_low=self.round_off(self.value_low) if self.value_low_calc == 'ABSOLUTE' else self.value_low_calc,
            value_high=self.round_off(self.value_high) if self.value_high_calc == 'ABSOLUTE' else self.value_high_calc,
            age_in_days=age_in_days,
            age_low_quantifier=self.age_low_quantifier,
            age_low_days=self.age_low_days(),
            age_high_quantifier=self.age_high_quantifier,
            age_high_days=self.age_high_days(),
            uln=' X ULN' if self.use_uln else '',
            lln='X LLN' if self.use_lln else '',
            fasting='Fasting' if self.fasting.lower() == 'yes' else '',
            serum='' if self.serum.lower() == 'n/a' else 'serum {0}'.format(self.serum),
            comment=self.comment,
            dummy='DUMMY' if self.dummy else '')

    def __unicode__(self):
        return '{0} {1}'.format(self.test_code.code, self.grade)

    class Meta:
        app_label = 'lab_clinic_reference'
        ordering = ['test_code', 'age_low', 'age_low_unit']
