from django.db import models


class VerificationFieldsMixin(models.Model):

    """A fields mixin for models that are verified against a
    paper document, such as an ICF.

    These fields are updated through an Admin action
    """

    is_verified = models.BooleanField(default=False, editable=False)

    is_verified_datetime = models.DateTimeField(null=True, editable=False)

    verified_by = models.CharField(max_length=25, null=True, editable=False)

    class Meta:
        abstract = True
