from django.db import models
from django.utils import timezone

from edc_constants.constants import OPEN, CLOSED, OTHER

from ...identifiers import ManifestIdentifier
from ...constants import SHIPPED
from edc_lab.constants import TESTING, STORAGE

STATUS = (
    (OPEN, 'Open'),
    (CLOSED, 'Closed'),
    (SHIPPED, 'Shipped'),
)

MANIFEST_CATEGORY = (
    (TESTING, 'Testing'),
    (STORAGE, 'Storage'),
    (OTHER, 'Other'),
)


class ManifestModelMixin(models.Model):

    manifest_identifier = models.CharField(
        verbose_name='Manifest Identifier',
        max_length=25,
        editable=False,
        unique=True)

    manifest_datetime = models.DateTimeField(
        default=timezone.now)

    status = models.CharField(
        max_length=15,
        default=OPEN,
        choices=STATUS)

    category = models.CharField(
        max_length=25,
        default=TESTING,
        choices=MANIFEST_CATEGORY)

    category_other = models.CharField(
        max_length=25,
        null=True,
        blank=True)

    comment = models.TextField(
        verbose_name='Comment',
        null=True)

    shipped = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.manifest_identifier:
            identifier = ManifestIdentifier(model=self.__class__)
            self.manifest_identifier = identifier.identifier
        self.shipped = True if self.status == SHIPPED else False
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.manifest_identifier, )

    @property
    def human_readable_identifier(self):
        x = self.manifest_identifier
        return '{}-{}-{}'.format(x[0:4], x[4:8], x[8:12])

    class Meta:
        abstract = True
        ordering = ('-manifest_identifier', )
