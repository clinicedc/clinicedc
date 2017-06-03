from django.core.validators import RegexValidator
from django.db import models
from edc_lab.lab.aliquot_type import AliquotType
from edc_lab.site_labs import site_labs


class AliquotTypeModelMixin(models.Model):

    aliquot_type = models.CharField(
        verbose_name='Aliquot Type Name',
        max_length=25)

    alpha_code = models.CharField(
        verbose_name='Aliquot Type Alpha Code',
        validators=[RegexValidator('^[A-Z]{2}$')],
        max_length=25)

    numeric_code = models.CharField(
        verbose_name='Aliquot Type Numeric Code',
        validators=[RegexValidator('^[0-9]{2}$')],
        max_length=25)

    @property
    def aliquot_type_object(self):
        return site_labs.get_aliquot_type(name=self.aliquot_type)

    class Meta:
        abstract = True
