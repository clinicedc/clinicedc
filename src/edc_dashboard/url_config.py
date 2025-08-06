from __future__ import annotations

from typing import TYPE_CHECKING, Type

from django.urls.conf import re_path
from edc_constants.constants import UUID_PATTERN

from .url_names import url_names

if TYPE_CHECKING:
    from django.urls import URLPattern
    from django.views import View as BaseView

    from .view_mixins import UrlRequestContextMixin

    class View(UrlRequestContextMixin, BaseView): ...


class UrlConfig:
    def __init__(
        self,
        url_name: str = None,
        namespace: str = None,
        view_class: Type[View | UrlRequestContextMixin] = None,
        label: str = None,
        identifier_label: str = None,
        identifier_pattern: str = None,
    ):
        self.identifier_label = identifier_label
        self.identifier_pattern = identifier_pattern
        self.label = label
        self.url_name = url_name
        self.view_class = view_class

        # register {urlname, namespace:urlname} with url_names
        url_names.register(url=self.url_name, namespace=namespace)

    @property
    def dashboard_urls(self) -> list[URLPattern]:
        """Returns url patterns."""
        urlpatterns = [
            re_path(
                "%(label)s/"
                "(?P<%(identifier_label)s>%(identifier_pattern)s)/"
                r"(?P<visit_schedule_name>\w+)/"
                r"(?P<schedule_name>\w+)/"
                r"(?P<visit_code>\w+)/"
                r"(?P<unscheduled>\w+)/"
                % {
                    "label": self.label,
                    "identifier_label": self.identifier_label,
                    "identifier_pattern": self.identifier_pattern,
                },
                self.view_class.as_view(),
                name=self.url_name,
            ),
            re_path(
                "%(label)s/"
                "(?P<%(identifier_label)s>%(identifier_pattern)s)/"
                r"(?P<visit_schedule_name>\w+)/"
                r"(?P<schedule_name>\w+)/"
                r"(?P<visit_code>\w+)/"
                % dict(
                    label=self.label,
                    identifier_label=self.identifier_label,
                    identifier_pattern=self.identifier_pattern,
                ),
                self.view_class.as_view(),
                name=self.url_name,
            ),
            re_path(
                "%(label)s/"
                "(?P<%(identifier_label)s>%(identifier_pattern)s)/"
                "(?P<appointment>%(uuid_pattern)s)/"
                r"(?P<scanning>\d)/"
                r"(?P<error>\d)/"
                % dict(
                    label=self.label,
                    identifier_label=self.identifier_label,
                    identifier_pattern=self.identifier_pattern,
                    uuid_pattern=UUID_PATTERN.pattern,
                ),
                self.view_class.as_view(),
                name=self.url_name,
            ),
            re_path(
                "%(label)s/"
                "(?P<%(identifier_label)s>%(identifier_pattern)s)/"
                "(?P<appointment>%(uuid_pattern)s)/"
                r"(?P<reason>\w+)/"
                % dict(
                    label=self.label,
                    identifier_label=self.identifier_label,
                    identifier_pattern=self.identifier_pattern,
                    uuid_pattern=UUID_PATTERN.pattern,
                ),
                self.view_class.as_view(),
                name=self.url_name,
            ),
            re_path(
                "%(label)s/"
                "(?P<%(identifier_label)s>%(identifier_pattern)s)/"
                "(?P<appointment>%(uuid_pattern)s)/"
                % dict(
                    label=self.label,
                    identifier_label=self.identifier_label,
                    identifier_pattern=self.identifier_pattern,
                    uuid_pattern=UUID_PATTERN.pattern,
                ),
                self.view_class.as_view(),
                name=self.url_name,
            ),
            re_path(
                "%(label)s/"
                "(?P<%(identifier_label)s>%(identifier_pattern)s)/"
                r"(?P<schedule_name>\w+)/"
                % dict(
                    label=self.label,
                    identifier_label=self.identifier_label,
                    identifier_pattern=self.identifier_pattern,
                ),
                self.view_class.as_view(),
                name=self.url_name,
            ),
            re_path(
                "%(label)s/(?P<%(identifier_label)s>%(identifier_pattern)s)/"
                % dict(
                    label=self.label,
                    identifier_label=self.identifier_label,
                    identifier_pattern=self.identifier_pattern,
                ),
                self.view_class.as_view(),
                name=self.url_name,
            ),
        ]
        return urlpatterns

    @property
    def listboard_urls(self) -> list[URLPattern]:
        """Returns url patterns.

        configs = [(listboard_url, listboard_view_class, label), (), ...]
        """
        urlpatterns = [
            re_path(
                "%(label)s/(?P<%(identifier_label)s>%(identifier_pattern)s)/"
                r"(?P<page>\d+)/"
                % dict(
                    label=self.label,
                    identifier_label=self.identifier_label,
                    identifier_pattern=self.identifier_pattern,
                ),
                self.view_class.as_view(),
                name=self.url_name,
            ),
            re_path(
                "%(label)s/(?P<%(identifier_label)s>%(identifier_pattern)s)/"
                % dict(
                    label=self.label,
                    identifier_label=self.identifier_label,
                    identifier_pattern=self.identifier_pattern,
                ),
                self.view_class.as_view(),
                name=self.url_name,
            ),
            re_path(
                r"%(label)s/(?P<page>\d+)/" % dict(label=self.label),
                self.view_class.as_view(),
                name=self.url_name,
            ),
            re_path(
                r"%(label)s/" % dict(label=self.label),
                self.view_class.as_view(),
                name=self.url_name,
            ),
        ]
        return urlpatterns

    @property
    def review_listboard_urls(self) -> list[URLPattern]:
        url_patterns = [
            re_path(
                "%(label)s/(?P<%(identifier_label)s>%(identifier_pattern)s)/"
                "(?P<appointment>%(uuid_pattern)s)/"
                % dict(
                    label=self.label,
                    identifier_label=self.identifier_label,
                    identifier_pattern=self.identifier_pattern,
                    uuid_pattern=UUID_PATTERN.pattern,
                ),
                self.view_class.as_view(),
                name=self.url_name,
            )
        ]
        url_patterns.extend(self.listboard_urls)
        return url_patterns
