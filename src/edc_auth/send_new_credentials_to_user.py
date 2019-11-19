from django.conf import settings
from django.core.mail.message import EmailMessage
from mempass.password_generator import PasswordGenerator
from urllib.parse import urlparse

from .import_users import change_user_template


def change_password(user, nwords=None):
    nwords = nwords or 4
    pwdgen = PasswordGenerator(nwords=nwords)
    password = pwdgen.get_password()
    user.set_password(password)
    user.save()
    return password


def send_new_credentials_to_user(user, request=None, nwords=None):
    body = change_user_template
    site_names = "\n".join([s.name for s in user.userprofile.sites.all()])
    role_names = "\n".join([r.display_name for r in user.userprofile.roles.all()])
    resource_name = urlparse(settings.INDEX_PAGE).netloc
    password = change_password(user, nwords)
    opts = {
        "resource_name": resource_name,
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
        f"Your {resource_name} user account has been updated.",
        body=body.safe_substitute(opts),
        from_email="noreply@clinicedc.org",
        to=(user.email,),
    ).send(fail_silently=True)
