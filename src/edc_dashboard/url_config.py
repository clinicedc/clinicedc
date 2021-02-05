from django.urls.conf import re_path
from edc_constants.constants import UUID_PATTERN

from .url_names import url_names


class UrlConfig:
    def __init__(
        self,
        url_name=None,
        namespace=None,
        view_class=None,
        label=None,
        identifier_label=None,
        identifier_pattern=None,
    ):
        self.identifier_label = identifier_label
        self.identifier_pattern = identifier_pattern
        self.label = label
        self.url_name = url_name
        self.view_class = view_class

        # register {urlname, namespace:urlname} with url_names
        url_names.register(url=self.url_name, namespace=namespace)

    @property
    def dashboard_urls(self):
        """Returns url patterns."""
        urlpatterns = [
            re_path(
                f"{self.label}/"
                f"(?P<{self.identifier_label}>{self.identifier_pattern})/"
                r"(?P<visit_schedule_name>\w+)/"
                r"(?P<schedule_name>\w+)/"
                r"(?P<visit_code>\w+)/"
                r"(?P<unscheduled>\w+)/",
                self.view_class.as_view(),
                name=self.url_name,
            ),
            re_path(
                f"{self.label}/"
                f"(?P<{self.identifier_label}>{self.identifier_pattern})/"
                r"(?P<visit_schedule_name>\w+)/"
                r"(?P<schedule_name>\w+)/"
                r"(?P<visit_code>\w+)/",
                self.view_class.as_view(),
                name=self.url_name,
            ),
            re_path(
                f"{self.label}/"
                f"(?P<{self.identifier_label}>{self.identifier_pattern})/"
                f"(?P<appointment>{UUID_PATTERN.pattern})/"
                r"(?P<scanning>\d)/"
                r"(?P<error>\d)/",
                self.view_class.as_view(),
                name=self.url_name,
            ),
            re_path(
                f"{self.label}/"
                f"(?P<{self.identifier_label}>{self.identifier_pattern})/"
                f"(?P<appointment>{UUID_PATTERN.pattern})/"
                r"(?P<reason>\w+)/",
                self.view_class.as_view(),
                name=self.url_name,
            ),
            re_path(
                f"{self.label}/"
                f"(?P<{self.identifier_label}>{self.identifier_pattern})/"
                f"(?P<appointment>{UUID_PATTERN.pattern})/",
                self.view_class.as_view(),
                name=self.url_name,
            ),
            re_path(
                f"{self.label}/"
                f"(?P<{self.identifier_label}>{self.identifier_pattern})/"
                r"(?P<schedule_name>\w+)/",
                self.view_class.as_view(),
                name=self.url_name,
            ),
            re_path(
                f"{self.label}/" f"(?P<{self.identifier_label}>{self.identifier_pattern})/",
                self.view_class.as_view(),
                name=self.url_name,
            ),
        ]
        return urlpatterns

    @property
    def listboard_urls(self):
        """Returns url patterns.

        configs = [(listboard_url, listboard_view_class, label), (), ...]
        """
        urlpatterns = [
            re_path(
                f"{self.label}/"
                f"(?P<{self.identifier_label}>{self.identifier_pattern})/"
                r"(?P<page>\d+)/",
                self.view_class.as_view(),
                name=self.url_name,
            ),
            re_path(
                f"{self.label}/" f"(?P<{self.identifier_label}>{self.identifier_pattern})/",
                self.view_class.as_view(),
                name=self.url_name,
            ),
            re_path(
                f"{self.label}" + r"/(?P<page>\d+)/",
                self.view_class.as_view(),
                name=self.url_name,
            ),
            re_path(f"{self.label}/", self.view_class.as_view(), name=self.url_name),
        ]
        return urlpatterns

    @property
    def review_listboard_urls(self):
        url_patterns = [
            re_path(
                f"{self.label}/"
                f"(?P<{self.identifier_label}>{self.identifier_pattern})/"
                f"(?P<appointment>{UUID_PATTERN.pattern})/",
                self.view_class.as_view(),
                name=self.url_name,
            )
        ]
        url_patterns.extend(self.listboard_urls)
        return url_patterns
