from django.db import models


class AddressMixin(models.Model):

    contact_name = models.CharField(max_length=50, null=True, blank=True)

    address = models.CharField(verbose_name="Address", max_length=50)

    postal_code = models.CharField(default="0000", max_length=50)

    city = models.CharField(max_length=50)

    state = models.CharField(
        verbose_name="State or Province", null=True, blank=True, max_length=50
    )

    country = models.CharField(max_length=50)

    telephone = models.CharField(null=True, blank=True, max_length=50)

    mobile = models.CharField(null=True, blank=True, max_length=50)

    fax = models.CharField(null=True, blank=True, max_length=50)

    email = models.EmailField(null=True, blank=True, max_length=50)

    class Meta:
        abstract = True
