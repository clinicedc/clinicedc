from django.apps import apps as django_apps


class AppConfigViewLookupError(Exception):
    pass


class AppConfigViewError(Exception):
    pass


class AppConfigViewMixin:

    """Adds url and template names for listboard and dashboard
    from app_config.
    """

    app_config_name = None  # AppConfig where urls names are defined
    listboard_url_name = None
    dashboard_url_name = None

    def __init__(self, **kwargs):
        self._base_template_name = None
        super().__init__(**kwargs)
        if not self.base_template_name:
            try:
                self.base_template_name = self.app_config.base_template_name
            except AttributeError as e:
                raise AppConfigViewError(f'{e}. {repr(self.app_config)}')
        if not self.dashboard_url_name:
            try:
                self.dashboard_url_name = self.app_config.dashboard_url_name
            except AttributeError as e:
                raise AppConfigViewError(f'{e}. {repr(self.app_config)}')
        if not self.listboard_url_name:
            try:
                self.listboard_url_name = self.app_config.listboard_url_name
            except AttributeError as e:
                raise AppConfigViewError(f'{e}. {repr(self.app_config)}')

    @property
    def app_config(self):
        """Returns AppConfig instance or raises AppConfigViewLookupError.
        """
        try:
            app_config = django_apps.get_app_config(self.app_config_name)
        except LookupError as e:
            raise AppConfigViewLookupError(
                f'{e}. app_config_name=\'{self.app_config_name}\'. See {repr(self)}.')
        return app_config

    @property
    def base_template_name(self):
        if not self._base_template_name:
            try:
                self._base_template_name = self.app_config.base_template_name
            except AttributeError as e:
                raise AppConfigViewError(f'{e}. {repr(self.app_config)}')
        return self._base_template_name

    def url_names(self, attrname):
        """Returns a list of <url attr name>, <url name>
        read from app_configs.

        for example:
            { 'plot_dashboard_listboard_url_name': 'plot_dashboard:listboard_url',
              'household_dashboard_listboard_url_name': 'household_dashboard:listboard_url',
              ...}
        """
        url_names = []
        for app_config in django_apps.get_app_configs():
            try:
                url_name = getattr(app_config, attrname)
            except AttributeError:
                continue
            key = f'{app_config.name}_{attrname}'
            url_names.append((key, url_name))
        return url_names

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({k: v for k, v in self.url_names('listboard_url_name')})
        context.update({k: v for k, v in self.url_names('dashboard_url_name')})
        context.update(
            base_template_name=self.base_template_name or 'edc_base/base.html')
        context.update(listboard_url_name=self.listboard_url_name)
        context.update(dashboard_url_name=self.dashboard_url_name)
        return context
