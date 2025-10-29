from clinicedc_constants import NULL_STRING
from django.db import models


class AddressModelMixin(models.Model):
    address_one = models.CharField(max_length=255, default=NULL_STRING, blank=True)

    address_two = models.CharField(max_length=255, default=NULL_STRING, blank=True)

    city = models.CharField(max_length=255, default=NULL_STRING, blank=True)

    postal_code = models.CharField(max_length=255, default=NULL_STRING, blank=True)

    state = models.CharField(max_length=255, default=NULL_STRING, blank=True)

    country = models.CharField(max_length=255, default=NULL_STRING, blank=True)

    class Meta:
        abstract = True


class ContactModelMixin(models.Model):
    email = models.EmailField(default=NULL_STRING, blank=True)

    email_alternative = models.EmailField(default=NULL_STRING, blank=True)

    telephone = models.CharField(max_length=15, default=NULL_STRING, blank=True)

    telephone_alternative = models.CharField(max_length=15, default=NULL_STRING, blank=True)

    class Meta:
        abstract = True
