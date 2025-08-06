import csv
from datetime import datetime

from django.contrib.auth.models import User


def export_users(path):
    path = path or f"edc_users_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    user = {
        "username": None,
        "password": None,
        "is_staff": None,
        "is_active": None,
        "first_name": None,
        "last_name": None,
        "job_title": None,
        "email": None,
        "mobile": None,
        "alternate_email": None,
        "site_names": None,
        "role_names": None,
    }

    with open(path, "w+") as f:
        writer = csv.DictWriter(f, fieldnames=user, delimiter="|")
        writer.writeheader()
        for user in User.objects.all().order_by("username"):
            site_names = ",".join([s.name for s in user.userprofile.sites.all()])
            role_names = ",".join([g.name for g in user.userprofile.roles.all()])
            user = {
                "username": user.username,
                "password": user.password,
                "is_staff": user.is_staff,
                "is_active": user.is_active,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "job_title": user.userprofile.job_title,
                "email": user.email,
                "mobile": user.userprofile.mobile,
                "alternate_email": user.userprofile.alternate_email,
                "site_names": site_names or "",
                "role_names": role_names or "",
            }
            writer.writerow(user)
    print(f"Done. See file `{path}` in the current directory.")
