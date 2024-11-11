from django.db import models


class AddressModelMixin(models.Model):

    address_one = models.CharField(max_length=255, null=True, blank=True)

    address_two = models.CharField(max_length=255, null=True, blank=True)

    city = models.CharField(max_length=255, null=True, blank=True)

    postal_code = models.CharField(max_length=255, null=True, blank=True)

    state = models.CharField(max_length=255, null=True, blank=True)

    country = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        abstract = True


class ContactModelMixin(models.Model):
    email = models.EmailField(null=True, blank=True)

    email_alternative = models.EmailField(null=True, blank=True)

    telephone = models.CharField(max_length=15, null=True, blank=True)

    telephone_alternative = models.CharField(max_length=15, null=True, blank=True)

    class Meta:
        abstract = True
