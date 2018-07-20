from django.db import models
from django.utils import timezone
from edc_base.sites.site_model_mixin import SiteModelMixin
from edc_base.utils import get_utcnow
from edc_constants.constants import OPEN, CLOSED, OTHER

from ....constants import TESTING, STORAGE
from ....identifiers import ManifestIdentifier

STATUS = (
    (OPEN, 'Open'),
    (CLOSED, 'Closed'),
)

MANIFEST_CATEGORY = (
    (TESTING, 'Testing'),
    (STORAGE, 'Storage'),
    (OTHER, 'Other'),
)


class ManifestModelMixin(SiteModelMixin, models.Model):

    manifest_identifier = models.CharField(
        verbose_name='Manifest Identifier',
        max_length=25,
        editable=False,
        unique=True)

    manifest_datetime = models.DateTimeField(
        default=timezone.now)

    export_datetime = models.DateTimeField(
        null=True,
        blank=True)

    export_references = models.TextField(
        null=True,
        blank=True)

    description = models.TextField(
        verbose_name='Description of contents',
        null=True,
        help_text='If blank will be automatically generated')

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

    printed = models.BooleanField(default=False)

    printed_datetime = models.DateTimeField(
        null=True,
        blank=True)

    def save(self, *args, **kwargs):
        if not self.manifest_identifier:
            identifier = ManifestIdentifier()
            self.manifest_identifier = identifier.identifier
        if self.shipped and not self.export_datetime:
            self.export_datetime = get_utcnow()
        elif not self.shipped:
            self.export_datetime = None
            self.printed = False
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.manifest_identifier, )
    natural_key.dependencies = ['sites.Site']

    @property
    def human_readable_identifier(self):
        x = self.manifest_identifier
        return '{}-{}-{}'.format(x[0:4], x[4:8], x[8:12])

    class Meta:
        abstract = True
        ordering = ('-manifest_identifier', )
