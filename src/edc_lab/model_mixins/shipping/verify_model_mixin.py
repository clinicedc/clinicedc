from django.db import models
from django.utils import timezone

from edc_constants.constants import OPEN

from ...constants import VERIFIED


class VerifyModelMixin(models.Model):
    verified = models.IntegerField(default=0)

    verified_datetime = models.DateTimeField(null=True)

    def unverify(self):
        self.verified = 0
        self.verified_datetime = None
        self.save()
        self.box.save()

    class Meta:
        abstract = True


class VerifyBoxModelMixin(VerifyModelMixin, models.Model):
    def update_verified(self):
        if self.status in [OPEN, VERIFIED]:
            if self.is_verified:
                self.verified = 1
                self.status = VERIFIED
                self.verified_datetime = timezone.now()
            else:
                self.verified = 0
                self.verified_datetime = None
                self.status = OPEN

    def unverify_box(self):
        if self.status in [OPEN, VERIFIED]:
            for box_item in self.boxitem_set.all():
                box_item.unverify()
                self.save()

    @property
    def is_verified(self):
        return not (
            self.boxitem_set.all().count() == 0
            or self.boxitem_set.filter(verified=False).exists()
        )

    class Meta:
        abstract = True
