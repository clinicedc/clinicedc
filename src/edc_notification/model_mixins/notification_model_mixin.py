from django.db import models


class NotificationModelMixin(models.Model):

    emailed = models.BooleanField(default=False)

    emailed_datetime = models.DateTimeField(null=True)

    class Meta:
        abstract = True
