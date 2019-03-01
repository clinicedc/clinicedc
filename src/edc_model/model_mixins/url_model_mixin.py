from django.apps import apps as django_apps
from django.urls import reverse
from django.db import models
from django.urls.exceptions import NoReverseMatch


class UrlModelMixinNoReverseMatch(Exception):
    pass


class UrlModelMixin(models.Model):

    ADMIN_SITE_NAME = None  # default is '{app_label}_admin'

    def get_absolute_url(self):
        try:
            if self.id:
                absolute_url = reverse(self.admin_url_name, args=(str(self.id),))
            else:
                absolute_url = reverse(self.admin_url_name)
        except NoReverseMatch as e:
            raise UrlModelMixinNoReverseMatch(
                f"Tried {self.admin_url_name}. Got {e}. "
                f"Perhaps define AppConfig.admin_site_name or "
                f"directly on model.ADMIN_SITE_NAME that refers to your "
                f"app specific admin site."
            )
        return absolute_url

    @property
    def admin_url_name(self):
        """Returns the django admin add or change url name
        (includes namespace).
        """
        mode = "change" if self.id else "add"
        return (
            f"{self.admin_site_name}:"
            f"{self._meta.app_label}_{self._meta.object_name.lower()}_{mode}"
        )

    @property
    def admin_site_name(self):
        """Returns the admin url namespace for this model.

        e.g. for module plot the default would be 'plot_admin'.
        """
        # model specific
        admin_site_name = self.ADMIN_SITE_NAME
        if not admin_site_name:
            app_label = self._meta.app_label
            try:
                # app specific
                admin_site_name = django_apps.get_app_config(app_label).admin_site_name
            except AttributeError:
                # default
                admin_site_name = f"{self._meta.app_label}_admin"
        return admin_site_name

    class Meta:
        abstract = True
