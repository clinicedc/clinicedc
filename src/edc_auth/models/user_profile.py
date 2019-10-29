from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.deletion import CASCADE
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from edc_notification.model_mixins import NotificationUserProfileModelMixin

from .role import Role


class UserProfile(NotificationUserProfileModelMixin, models.Model):

    user = models.OneToOneField(User, on_delete=CASCADE)

    sites = models.ManyToManyField(Site, blank=True)

    job_title = models.CharField(max_length=100, null=True, blank=True)

    alternate_email = models.EmailField(
        _("Alternate email address"), blank=True, null=True
    )

    mobile = models.CharField(
        max_length=25,
        validators=[RegexValidator(regex="^\+\d+")],
        null=True,
        blank=True,
        help_text="e.g. +1234567890",
    )

    clinic_label_printer = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text=mark_safe(
            f'Change in <a href="/edc_label/">Edc Label Administration</a>'
        ),
    )

    lab_label_printer = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text=mark_safe(
            f'Change in <a href="/edc_label/">Edc Label Administration</a>'
        ),
    )

    print_server = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text=mark_safe(
            f'Change in <a href="/edc_label/">Edc Label Administration</a>'
        ),
    )

    roles = models.ManyToManyField(Role, blank=True)

    def __str__(self):
        return self.user.username
