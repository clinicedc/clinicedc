from django.contrib.auth.models import Group, User
from django.contrib.sites.models import Site
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.deletion import CASCADE
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from edc_export.choices import EXPORT_FORMATS
from edc_export.constants import CSV
from edc_notification.model_mixins import NotificationUserProfileModelMixin

from ..auth_objects import CUSTOM_ROLE, STAFF_ROLE
from .role import Role


class UserProfile(NotificationUserProfileModelMixin, models.Model):
    id = models.AutoField(primary_key=True)

    user = models.OneToOneField(User, on_delete=CASCADE)

    sites = models.ManyToManyField(Site, blank=True)

    job_title = models.CharField(max_length=100, null=True, blank=True)

    alternate_email = models.EmailField(_("Alternate email address"), blank=True, null=True)

    mobile = models.CharField(
        max_length=25,
        validators=[RegexValidator(regex=r"^\+\d+")],
        null=True,
        blank=True,
        help_text="e.g. +1234567890",
    )

    clinic_label_printer = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text=format_html('Change in <a href="/edc_label/">Edc Label Administration</a>'),
    )

    lab_label_printer = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text=format_html('Change in <a href="/edc_label/">Edc Label Administration</a>'),
    )

    print_server = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text=format_html('Change in <a href="/edc_label/">Edc Label Administration</a>'),
    )

    export_format = models.CharField(
        verbose_name="Export format",
        max_length=25,
        choices=EXPORT_FORMATS,
        default=CSV,
        null=True,
        blank=True,
        help_text="Note: requires export permissions",
    )

    roles = models.ManyToManyField(Role, blank=True)

    def __str__(self):
        return self.user.username

    def add_groups_for_roles(self, pk_set):
        """Add groups to this user for the selected roles.

        Called by m2m signal.
        """
        if CUSTOM_ROLE not in [obj.name for obj in self.roles.all()]:
            group_names = [group.name for group in self.user.groups.all()]
            add_group_names = []
            for role in self.roles.all():
                for group in role.groups.all():
                    if group.name not in group_names:
                        add_group_names.append(group.name)
            add_group_names = list(set(add_group_names))
            for name in add_group_names:
                self.user.groups.add(Group.objects.get(name=name))
                self.user.save()

    def remove_groups_for_roles(self, pk_set):
        """Remove groups from this user for the removed roles.

        Called by m2m signal.
        """
        if CUSTOM_ROLE in [obj.name for obj in Role.objects.filter(pk__in=pk_set)]:
            self.user.groups.clear()
            self.user.userprofile.roles.clear()
            self.user.userprofile.roles.add(Role.objects.get(name=STAFF_ROLE))
        else:
            remove_group_names = []
            current_group_names = []
            for role in self.roles.all():
                current_group_names.extend([group.name for group in role.groups.all()])
            for role in Role.objects.filter(pk__in=pk_set):
                remove_group_names.extend(
                    [
                        group.name
                        for group in role.groups.all()
                        if group.name not in current_group_names
                    ]
                )
            for name in remove_group_names:
                self.user.groups.remove(Group.objects.get(name=name))
