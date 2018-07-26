from django.contrib.auth.models import User
from django.db import models
from django.db.models.deletion import PROTECT
from django.utils.safestring import mark_safe


class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=PROTECT)

    study_site = models.CharField(
        max_length=100,
        blank=True,
        null=True)

    study_country = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='user\'s country of work')

    country = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='user\'s country of origin')

    clinic_label_printer = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text=mark_safe(f'Change in <a href="/edc_label/">Edc Label Administration</a>'))

    lab_label_printer = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text=mark_safe(f'Change in <a href="/edc_label/">Edc Label Administration</a>'))

    print_server = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text=mark_safe(f'Change in <a href="/edc_label/">Edc Label Administration</a>'))

    class Meta:
        # TODO: remove
        db_table = 'edc_base_userprofile'
