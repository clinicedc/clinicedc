from django.contrib.auth.models import User


def get_sites_from_user(user: User) -> list[int]:
    return [site.id for site in user.userprofile.sites.all()]
