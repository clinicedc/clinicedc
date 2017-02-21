from django.apps import apps as django_apps


class AppConfigViewMixin:

    """Adds url and template names for listboard and dashboard
    from app_config.
    """

    app_config_name = None
    base_template_name = None
    listboard_url_name = None
    dashboard_url_name = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.base_template_name:
            try:
                self.base_template_name = django_apps.get_app_config(
                    self.app_config_name).base_template_name
            except (AttributeError, LookupError):
                pass
        if not self.dashboard_url_name:
            try:
                self.dashboard_url_name = django_apps.get_app_config(
                    self.app_config_name).dashboard_url_name
            except (AttributeError, LookupError):
                pass
        if not self.listboard_url_name:
            try:
                self.listboard_url_name = django_apps.get_app_config(
                    self.app_config_name).listboard_url_name
            except (AttributeError, LookupError):
                pass

    def url_names(self, attrname):
        """Returns a generator of <url attr name>, <url name>
        read from app_configs.

        for example:
            { 'plot_listboard_url_name': 'plot:listboard_url',
              'household_listboard_url_name': 'household:listboard_url',
              ...}
        """
        for app_config in django_apps.get_app_configs():
            try:
                url_name = getattr(app_config, attrname)
            except AttributeError:
                continue
            key = '{}_{}'.format(app_config.name, attrname)
            yield key, url_name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({k: v for k, v in self.url_names('listboard_url_name')})
        context.update({k: v for k, v in self.url_names('dashboard_url_name')})
        context.update(
            base_template_name=self.base_template_name or 'edc_base/base.html')
        context.update(listboard_url_name=self.listboard_url_name)
        context.update(dashboard_url_name=self.dashboard_url_name)
        return context
