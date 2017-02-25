from django.db import models


class VerifyModelMixin(models.Model):

    verified = models.IntegerField(default=0)

    verified_datetime = models.DateTimeField(
        null=True)

    def unverify_box(self):
        try:
            box_items = self.boxitem_set.all()
        except AttributeError:
            pass
        else:
            for box_item in box_items:
                box_item.unverify()
            self.unverify()

    def unverify(self):
        self.verified = 0
        self.verified_datetime = None
        self.save()

    class Meta:
        abstract = True
