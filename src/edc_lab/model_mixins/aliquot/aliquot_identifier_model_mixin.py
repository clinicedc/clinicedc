from django.db import models


class AliquotIdentifierModelMixin(models.Model):

    # NOTE: aliquot_identifier is allocated by the Specimen object
    aliquot_identifier = models.CharField(
        max_length=25,
        unique=True)

    parent_identifier = models.CharField(
        verbose_name='Parent aliquot Identifier',
        max_length=25,
        editable=False)

    identifier_prefix = models.CharField(
        max_length=50,
        editable=False)

    subject_identifier = models.CharField(
        max_length=50,
        null=True,
        editable=False)

    requisition_identifier = models.CharField(
        max_length=50,
        null=True,
        editable=False)

    class Meta:
        abstract = True
