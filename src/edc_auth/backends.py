from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()


class ModelBackendWithSite(ModelBackend):
    """An authentication backend to only allow a login
    associated with the current SITE_ID.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username=username, password=password)
        if user:
            sites = [obj.id for obj in user.userprofile.sites.all()]
            try:
                site_id = request.site.id
            except AttributeError:
                site_id = settings.SITE_ID
            if user.is_superuser or site_id in sites:
                return user
        return None
