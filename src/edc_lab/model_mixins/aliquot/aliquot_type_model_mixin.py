from django.core.validators import RegexValidator
from django.db import models


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

    class Meta:
        abstract = True
