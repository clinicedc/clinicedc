from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from string import Template

from mempass import PasswordGenerator


class PasswordSetter:

    email_body_template = Template(
        "Hi $first_name, \n\n"
        "Your clinicedc.org password has been reset.\n\n"
        "Your new password is:\n\n$password\n\n"
        "Thanks.\n\n"
    )

    def __init__(self, alternate_email=None, nwords=None, **kwargs):
        self.alternate_email = alternate_email
        self.password_generator = PasswordGenerator(nwords=nwords, **kwargs)

    def reset_all(self):
        users = User.objects.filter(is_active=True, is_staff=True, is_superuser=False)
        self._reset(users)

    def reset_by_groups(self, group_names=None):
        users = User.objects.filter(
            groups__name__in=group_names,
            is_active=True,
            is_staff=True,
            is_superuser=False,
        )
        self._reset(users)

    def reset_users(self, usernames=None):
        users = User.objects.filter(
            username__in=usernames, is_active=True, is_staff=True
        )
        self._reset(users)

    def reset_by_sites(self, site_names=None, **kwargs):
        users = User.objects.filter(
            userprofile__sites__name__in=site_names,
            is_active=True,
            is_staff=True,
            is_superuser=False,
        )
        self._reset(users)

    def _reset(self, users):
        for user in users:
            password = self.password_generator.get_password()
            user.set_password(password)
            user.save()
            body = self.email_body_template.safe_substitute(
                first_name=user.first_name, password=password
            )
            email = EmailMessage(
                subject="Your clinicedc.org password has been reset.",
                body=body,
                from_email="noreply@clinicedc.org",
                to=[self.alternate_email if self.alternate_email else user.email],
            )
            email.send()
