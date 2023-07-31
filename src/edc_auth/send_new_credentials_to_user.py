from typing import Optional
from urllib.parse import urlparse

from django.core.mail.message import EmailMessage
from edc_dashboard.utils import get_index_page
from edc_protocol import Protocol
from mempass.password_generator import PasswordGenerator

from .import_users import change_user_template


def change_password(user, nwords: Optional[int] = None) -> str:
    nwords = nwords or 4
    pwdgen = PasswordGenerator(nwords=nwords)
    password = pwdgen.get_password()
    user.set_password(password)
    user.save()
    return password


def send_new_credentials_to_user(user, nwords: Optional[int] = None) -> EmailMessage:
    body = change_user_template
    site_names = "\n - ".join([s.name for s in user.userprofile.sites.all()])
    role_names = "\n - ".join([r.display_name for r in user.userprofile.roles.all()])
    resource_name = urlparse(get_index_page()).netloc
    project_name = Protocol().project_name
    password = change_password(user, nwords)
    opts = {
        "resource_name": resource_name,
        "project_name": project_name,
        "username": user.username,
        "password": password,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "job_title": user.userprofile.job_title or "?job title?",
        "email": user.email,
        "site_names": site_names or "None",
        "role_names": role_names or "None",
    }
    return EmailMessage(
        f"{project_name} EDC: Your {resource_name} user account has been updated.",
        body=body.safe_substitute(opts),
        from_email="noreply@clinicedc.org",
        to=(user.email,),
    ).send(fail_silently=True)
