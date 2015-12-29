from django.db import models
from edc_base.model.models import BaseUuidModel


class StudySiteManager(models.Manager):

    def get_by_natural_key(self, site_code):
        return self.get(site_code=site_code,)


class StudySite(BaseUuidModel):

    site_code = models.CharField(max_length=4, unique=True)

    site_name = models.CharField(max_length=75, unique=True)

    objects = StudySiteManager()

    def natural_key(self):
        return (self.site_code, )

    def __unicode__(self):
        return "%s %s" % (self.site_code, self.site_name)

    class Meta:
        unique_together = [('site_code', 'site_name')]
        ordering = ['site_code', ]
        app_label = 'edc_consent'
        db_table = 'bhp_variables_studysite'  # remove??
