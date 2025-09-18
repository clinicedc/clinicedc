from django.db import models


class AddressModelMixin(models.Model):
    address_one = models.CharField(max_length=255, default="", blank=True)

    address_two = models.CharField(max_length=255, default="", blank=True)

    city = models.CharField(max_length=255, default="", blank=True)

    postal_code = models.CharField(max_length=255, default="", blank=True)

    state = models.CharField(max_length=255, default="", blank=True)

    country = models.CharField(max_length=255, default="", blank=True)

    class Meta:
        abstract = True


class ContactModelMixin(models.Model):
    email = models.EmailField(default="", blank=True)

    email_alternative = models.EmailField(default="", blank=True)

    telephone = models.CharField(max_length=15, default="", blank=True)

    telephone_alternative = models.CharField(max_length=15, default="", blank=True)

    class Meta:
        abstract = True
