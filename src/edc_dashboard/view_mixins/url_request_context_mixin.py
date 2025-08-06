from __future__ import annotations

from typing import TYPE_CHECKING

from edc_protocol.research_protocol_config import ResearchProtocolConfig
from edc_utils.text import convert_from_camel

from ..url_config import UrlConfig
from ..url_names import InvalidDashboardUrlName, url_names

if TYPE_CHECKING:
    from django.urls import URLPattern


class UrlRequestContextError(Exception):
    pass


class UrlRequestContextMixin:
    urlconfig_getattr = "dashboard_urls"
    urlconfig_identifier_label = "subject_identifier"
    urlconfig_identifier_pattern = ResearchProtocolConfig().subject_identifier_pattern
    urlconfig_label = None
    url_name = None

    @classmethod
    def get_urlname(cls):
        return cls.url_name

    @classmethod
    def urls(
        cls,
        namespace: str = None,
        label: str = None,
        identifier_label: str = None,
        identifier_pattern: str = None,
    ) -> list[URLPattern]:
        label = (
            label
            or cls.urlconfig_label
            or convert_from_camel(cls.__name__.replace("view", "")).lower()
        )
        urlconfig = UrlConfig(
            url_name=cls.get_urlname(),
            namespace=namespace,
            view_class=cls,
            label=label,
            identifier_label=identifier_label or cls.urlconfig_identifier_label,
            identifier_pattern=identifier_pattern or cls.urlconfig_identifier_pattern,
        )
        return getattr(urlconfig, cls.urlconfig_getattr)

    @staticmethod
    def add_url_to_context(new_key=None, existing_key=None) -> dict[str, str]:
        """Add url as new_key to the context using the value
        of the existing_key from request.context_data.
        """
        try:
            url_data = {new_key: url_names.get(existing_key)}
        except InvalidDashboardUrlName as e:
            raise UrlRequestContextError(
                f"Url name not defined in url_names. "
                f"Expected one of {url_names.registry}. Got {e}. "
                f"Hint: check if dashboard middleware is loaded."
            )
        return url_data
