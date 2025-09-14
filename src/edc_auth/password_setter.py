from string import Template

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from mempass import PasswordGenerator

from edc_protocol.research_protocol_config import ResearchProtocolConfig


class PasswordSetterError(Exception):
    pass


class PasswordSetter:
    email_body_template = Template(
        "Hi $first_name, \n\n"
        "Your clinicedc.org password has been reset.\n\n"
        "Your new password is:\n\n$password\n\n"
        "Your password was reset by $administrator.\n\n"
        "Thanks.\n\n"
        f"{ResearchProtocolConfig().project_name}\n\n"
    )

    def __init__(
        self,
        super_username: str,
        alternate_email: str | None = None,
        nwords: int | None = None,
        **kwargs,
    ) -> None:
        self.administrator_fullname = self.get_administrator_fullname(super_username)
        self.alternate_email = alternate_email
        self.password_generator = PasswordGenerator(nwords=nwords, **kwargs)

    @staticmethod
    def get_administrator_fullname(super_username: str) -> str:
        try:
            obj = User.objects.get(username=super_username)
        except ObjectDoesNotExist:
            raise PasswordSetterError(
                "Need the username of the administrator / super user. Got None."
            )
        return f"{obj.first_name} {obj.last_name}"

    def reset_all(self) -> None:
        users = User.objects.filter(is_active=True, is_staff=True, is_superuser=False)
        self._reset(users)

    def reset_by_groups(self, group_names: list[str] = None) -> None:
        users = User.objects.filter(
            groups__name__in=group_names,
            is_active=True,
            is_staff=True,
            is_superuser=False,
        )
        self._reset(users)

    def reset_users(self, usernames: list[str]) -> None:
        users = User.objects.filter(username__in=usernames, is_active=True, is_staff=True)
        self._reset(users)

    def reset_user(self, username: str) -> None:
        usernames = [username]
        self.reset_users(usernames)

    def reset_by_sites(self, site_names: list[str] = None) -> None:
        users = User.objects.filter(
            userprofile__sites__name__in=site_names,
            is_active=True,
            is_staff=True,
            is_superuser=False,
        )
        self._reset(users)

    def _reset(self, users: list[User]) -> None:
        for user in users:
            password = self.password_generator.get_password()
            user.set_password(password)
            user.save()
            body = self.email_body_template.safe_substitute(
                first_name=user.first_name,
                password=password,
                administrator=self.administrator_fullname,
            )
            email = EmailMessage(
                subject=(
                    f"{ResearchProtocolConfig().project_name}: "
                    "Your clinicedc.org password has been reset."
                ),
                body=body,
                from_email="noreply@clinicedc.org",
                to=[self.alternate_email if self.alternate_email else user.email],
            )
            email.send()
