from django.db import models
from django.db.models import options

from edc_protocol.mixins import SubjectTypeCapMixin

options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('subject_type_name', )


class SubjectTypeCapModelMixin(SubjectTypeCapMixin, models.Model):

    """Blocks new instances once a record count is reached."""

    cap_count = models.IntegerField(editable=False)

    cap = models.IntegerField(editable=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.cap_count, self.cap = self.fetch_or_raise_on_cap_met()
        super(SubjectTypeCapModelMixin, self).save(*args, **kwargs)

    class Meta:
        abstract = True
        subject_type_name = None
