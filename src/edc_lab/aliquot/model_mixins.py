from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

from edc_base.model.models.list_model_mixin import ListModelMixin
from edc_lab.choices import ALIQUOT_STATUS, SPECIMEN_MEASURE_UNITS, SPECIMEN_MEDIUM

from .site_aliquot_profiles import site_lab_profiles


class AliquotModelMixin (models.Model):

    aliquot_identifier = models.CharField(
        verbose_name='Aliquot Identifier',
        max_length=25,
        unique=True,
        help_text="Aliquot identifier",
        editable=False)

    aliquot_datetime = models.DateTimeField(
        verbose_name="Date and time aliquot created",
        default=timezone.now)

    aliquot_type = models.CharField(
        verbose_name='Aliquot Type',
        validators=[RegexValidator('\d+')],
        max_length=25)

    is_primary = models.BooleanField(
        default=False,
        editable=False)

    parent_identifier = models.CharField(
        verbose_name='Parent aliquot Identifier',
        max_length=25,
        editable=False)

    specimen_identifier = models.CharField(
        verbose_name='Specimen Id',
        max_length=50,
        editable=False)

    count = models.IntegerField(
        editable=False,
        help_text='pos in sequence of aliquots from parent')

    medium = models.CharField(
        verbose_name='Medium',
        max_length=25,
        choices=SPECIMEN_MEDIUM,
        default='TUBE')

    medium_count = models.IntegerField(
        editable=False,
        default=1,
        help_text='e.g. number of tubes')

    original_measure = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default='5.00')

    current_measure = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default='5.00')

    measure_units = models.CharField(
        max_length=25,
        choices=SPECIMEN_MEASURE_UNITS,
        default='mL')

    status = models.CharField(
        max_length=25,
        choices=ALIQUOT_STATUS,
        default='available')

    comment = models.CharField(
        max_length=50,
        null=True,
        blank=True)

    def __str__(self):
        return '%s' % (self.aliquot_identifier)

    def natural_key(self):
        return (self.aliquot_identifier,)

    class Meta:
        abstract = True


class AliquotConditionModelMixin(ListModelMixin):

    def __str__(self):
        return "{0}: {1}".format(self.short_name.upper(), self.name)

    class Meta:
        ordering = ["name"]
        abstract = True


class AliquotTypeModelMixin(ListModelMixin):

    alpha_code = models.CharField(
        verbose_name='Alpha code',
        validators=[
            RegexValidator('^[A-Z]{2,15}$')
        ],
        max_length=15,
        unique=True,
    )
    numeric_code = models.CharField(
        verbose_name='Numeric code (2-digit)',
        max_length=2,
        validators=[
            RegexValidator('^[0-9]{2}$')
        ],
        unique=True,
    )

    def __str__(self):
        return "{0} {1}: {2}".format(self.alpha_code, self.numeric_code, self.name.lower())

    def natural_key(self):
        return (self.alpha_code, self.numeric_code)

    class Meta:
        ordering = ["name"]
        unique_together = (('alpha_code', 'numeric_code'), )
        abstract = True


class AliquotMediumModelMixin(ListModelMixin):

    def __str__(self):
        return "%s" % (self.name.upper())

    class Meta:
        ordering = ["name"]
        abstract = True


class AliquotProcessingModelMixin(models.Model):

    print_labels = models.BooleanField(
        verbose_name='Print aliquot labels now',
        default=True,
        help_text='If checked, labels will be printed immediately.')

    objects = models.Manager()

    def __str__(self):
        return self.aliquot.aliquot_identifier

    def save(self, *args, **kwargs):
        aliquot_profile = site_lab_profiles.registry.get(self.aliquot.receive.requisition_model_name)
        aliquot_profile().aliquot_by_profile(self.aliquot, self.profile)
        super(AliquotProcessingModelMixin, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class AliquotProfileItemModelMixin(models.Model):

    volume = models.DecimalField(verbose_name='Volume (ml)', max_digits=10, decimal_places=1, null=True)

    count = models.IntegerField(verbose_name='aliquots to create')

    class Meta:
        abstract = True


class AliquotProfileModelMixin(models.Model):

    name = models.CharField(
        verbose_name='Profile Name',
        max_length=50,
        unique=True)

    objects = models.Manager()

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True
