from __future__ import annotations

from typing import TYPE_CHECKING

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
        *,
        url_name: str,
        namespace: str,
        view_class: type[View | UrlRequestContextMixin],
        label: str,
        identifier_label: str,
        identifier_pattern: str,
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
        return [
            re_path(
                "{label}/"
                "(?P<{identifier_label}>{identifier_pattern})/"
                r"(?P<visit_schedule_name>\w+)/"
                r"(?P<schedule_name>\w+)/"
                r"(?P<visit_code>\w+)/"
                r"(?P<unscheduled>\w+)/".format(
                    **dict(
                        label=self.label,
                        identifier_label=self.identifier_label,
                        identifier_pattern=self.identifier_pattern,
                    )
                ),
                self.view_class.as_view(),
                name=self.url_name,
            ),
            re_path(
                "{label}/"
                "(?P<{identifier_label}>{identifier_pattern})/"
                r"(?P<visit_schedule_name>\w+)/"
                r"(?P<schedule_name>\w+)/"
                r"(?P<visit_code>\w+)/".format(
                    **dict(
                        label=self.label,
                        identifier_label=self.identifier_label,
                        identifier_pattern=self.identifier_pattern,
                    )
                ),
                self.view_class.as_view(),
                name=self.url_name,
            ),
            re_path(
                "{label}/"
                "(?P<{identifier_label}>{identifier_pattern})/"
                "(?P<appointment>{uuid_pattern})/"
                r"(?P<scanning>\d)/"
                r"(?P<error>\d)/".format(
                    **dict(
                        label=self.label,
                        identifier_label=self.identifier_label,
                        identifier_pattern=self.identifier_pattern,
                        uuid_pattern=UUID_PATTERN.pattern,
                    )
                ),
                self.view_class.as_view(),
                name=self.url_name,
            ),
            re_path(
                "{label}/"
                "(?P<{identifier_label}>{identifier_pattern})/"
                "(?P<appointment>{uuid_pattern})/"
                r"(?P<reason>\w+)/".format(
                    **dict(
                        label=self.label,
                        identifier_label=self.identifier_label,
                        identifier_pattern=self.identifier_pattern,
                        uuid_pattern=UUID_PATTERN.pattern,
                    )
                ),
                self.view_class.as_view(),
                name=self.url_name,
            ),
            re_path(
                "{label}/"
                "(?P<{identifier_label}>{identifier_pattern})/"
                "(?P<appointment>{uuid_pattern})/".format(
                    **dict(
                        label=self.label,
                        identifier_label=self.identifier_label,
                        identifier_pattern=self.identifier_pattern,
                        uuid_pattern=UUID_PATTERN.pattern,
                    )
                ),
                self.view_class.as_view(),
                name=self.url_name,
            ),
            re_path(
                "{label}/"
                "(?P<{identifier_label}>{identifier_pattern})/"
                r"(?P<schedule_name>\w+)/".format(
                    **dict(
                        label=self.label,
                        identifier_label=self.identifier_label,
                        identifier_pattern=self.identifier_pattern,
                    )
                ),
                self.view_class.as_view(),
                name=self.url_name,
            ),
            re_path(
                "{label}/(?P<{identifier_label}>{identifier_pattern})/".format(
                    **dict(
                        label=self.label,
                        identifier_label=self.identifier_label,
                        identifier_pattern=self.identifier_pattern,
                    )
                ),
                self.view_class.as_view(),
                name=self.url_name,
            ),
        ]

    @property
    def listboard_urls(self) -> list[URLPattern]:
        """Returns url patterns.

        configs = [(listboard_url, listboard_view_class, label), (), ...]
        """
        return [
            re_path(
                "{label}/(?P<{identifier_label}>{identifier_pattern})/"
                r"(?P<page>\d+)/".format(
                    **dict(
                        label=self.label,
                        identifier_label=self.identifier_label,
                        identifier_pattern=self.identifier_pattern,
                    )
                ),
                self.view_class.as_view(),
                name=self.url_name,
            ),
            re_path(
                "{label}/(?P<{identifier_label}>{identifier_pattern})/".format(
                    **dict(
                        label=self.label,
                        identifier_label=self.identifier_label,
                        identifier_pattern=self.identifier_pattern,
                    )
                ),
                self.view_class.as_view(),
                name=self.url_name,
            ),
            re_path(
                r"{label}/(?P<page>\d+)/".format(**dict(label=self.label)),
                self.view_class.as_view(),
                name=self.url_name,
            ),
            re_path(
                r"{label}/".format(**dict(label=self.label)),
                self.view_class.as_view(),
                name=self.url_name,
            ),
        ]

    @property
    def review_listboard_urls(self) -> list[URLPattern]:
        url_patterns = [
            re_path(
                "{label}/(?P<{identifier_label}>{identifier_pattern})/"
                "(?P<appointment>{uuid_pattern})/".format(
                    **dict(
                        label=self.label,
                        identifier_label=self.identifier_label,
                        identifier_pattern=self.identifier_pattern,
                        uuid_pattern=UUID_PATTERN.pattern,
                    )
                ),
                self.view_class.as_view(),
                name=self.url_name,
            )
        ]
        url_patterns.extend(self.listboard_urls)
        return url_patterns
