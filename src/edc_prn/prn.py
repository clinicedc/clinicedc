from django.apps import apps as django_apps


class Prn:

    def __init__(self, model=None, url_namespace=None, allow_add=None,
                 verbose_name=None, show_on_dashboard=None):

        self._verbose_name = verbose_name
        self.url_namespace = url_namespace or ''
        self.allow_add = allow_add
        self.model = model
        self.show_on_dashboard = show_on_dashboard

        self.url_name = '_'.join(self.model.split('.'))
        sep = ':' if self.url_namespace else ''
        self.add_url_name = None
        if self.allow_add:
            self.add_url_name = f'{self.url_namespace}{sep}{self.url_name}_add'
        self.changelist_url_name = f'{self.url_namespace}{sep}{self.url_name}_changelist'

    @property
    def verbose_name(self):
        if not self._verbose_name:
            self._verbose_name = self.model_cls._meta.verbose_name
        return self._verbose_name

    @property
    def model_cls(self):
        return django_apps.get_model(self.model)
