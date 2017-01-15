from django.apps import apps as django_apps


class AppConfigViewMixin:

    """Adds url and template names for listboard and dashboard from app_config"""

    app_config_name = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # add listboard url name
        context.update(listboard_url_name=self.listboard_url_name)
        context.update({
            '{}_listboard_url_name'.format(self.app_config_name):
            self.listboard_url_name})
        # try to add dashboard url name
        try:
            context.update(dashboard_url_name=self.dashboard_url_name)
        except AttributeError:
            pass
        else:
            context.update(
                {'{}_dashboard_url_name'.format(self.app_config_name): self.dashboard_url_name})
        # try to add dashboard base template name
        try:
            context.update(base_template_name=self.base_template_name)
        except AttributeError:
            context.update(base_template_name='edc_base/base.html')
        return context

    @property
    def listboard_url_name(self):
        return django_apps.get_app_config(self.app_config_name).listboard_url_name

    @property
    def dashboard_url_name(self):
        return django_apps.get_app_config(self.app_config_name).dashboard_url_name

    @property
    def base_template_name(self):
        return django_apps.get_app_config(self.app_config_name).base_template_name
