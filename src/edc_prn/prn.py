from django.apps import apps as django_apps
from django.core.exceptions import FieldError


class PrnError(Exception):
    pass


class Prn:
    def __init__(
        self,
        model=None,
        url_namespace=None,
        allow_add=None,
        verbose_name=None,
        verbose_name_plural=None,
        show_on_dashboard=None,
        dashboard_url_name=None,
        fa_icon=None,
    ):
        self._verbose_name = verbose_name
        self._verbose_name_plural = verbose_name_plural
        self.url_namespace = url_namespace or ""
        self.allow_add = allow_add
        self.fa_icon = fa_icon
        self.model = model
        self.add_button_id = f"{'_'.join(model.split('.'))}_add"
        self.dashboard_url_name = dashboard_url_name  # next url
        self.show_on_dashboard = True if show_on_dashboard is None else show_on_dashboard

        self.url_name = "_".join(self.model.split("."))
        sep = ":" if self.url_namespace else ""
        self.add_url_name = None
        if self.allow_add:
            self.add_url_name = f"{self.url_namespace}{sep}{self.url_name}_add"
        self.changelist_url_name = f"{self.url_namespace}{sep}{self.url_name}_changelist"

    def __repr__(self):
        return f"{self.__class__.__name__}(model={self.model})"

    def __str__(self):
        return self.model

    @property
    def verbose_name(self):
        if not self._verbose_name:
            self._verbose_name = self.model_cls._meta.verbose_name
        return self._verbose_name

    @property
    def verbose_name_plural(self):
        if not self._verbose_name_plural:
            self._verbose_name_plural = self.model_cls._meta.verbose_name_plural
        return self._verbose_name_plural

    @property
    def model_cls(self):
        try:
            return django_apps.get_model(self.model)
        except LookupError as e:
            raise PrnError(f"{e}. See {repr(self)}")

    def get_show_on_dashboard(self, subject_identifier=None, **kwargs):
        count = 0
        if self.show_on_dashboard:
            if subject_identifier:
                opts = dict(subject_identifier=subject_identifier)
                try:
                    count = self.model_cls.objects.filter(**opts).count()
                except FieldError:
                    opts = self.get_query_opts(subject_identifier)
                    count = self.model_cls.objects.filter(**opts).count()
        return True if count and self.show_on_dashboard else False

    def get_query_opts(self, subject_identifier):
        """Returns alternative query opts to search on
        subject_identifier.

        Called after a simple subject identifier lookup fails
        """
        try:
            attr = self.model_cls.related_visit_model_attr()
            opts = {f"{attr}__subject_identifier": subject_identifier}
        except AttributeError:
            opts = {"registered_subject__subject_identifier": subject_identifier}
        return opts
