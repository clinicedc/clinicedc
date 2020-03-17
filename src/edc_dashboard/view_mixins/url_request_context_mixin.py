from django.apps import apps as django_apps
from django.views.generic.base import ContextMixin
from edc_protocol import Protocol
from edc_utils.text import convert_from_camel

from ..url_config import UrlConfig
from ..url_names import InvalidUrlName, url_names


class UrlRequestContextError(Exception):
    pass


class UrlRequestContextMixin(ContextMixin):

    urlconfig_getattr = "dashboard_urls"
    urlconfig_identifier_label = "subject_identifier"
    urlconfig_identifier_pattern = Protocol().subject_identifier_pattern
    urlconfig_label = None

    @classmethod
    def get_urlname(cls):
        raise NotImplementedError

    @classmethod
    def urls(
        cls, namespace=None, label=None, identifier_label=None, identifier_pattern=None
    ):
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

    def add_url_to_context(self, new_key=None, existing_key=None, context=None):
        """Add a url as new_key to the context using the value
        of the existing_key from request.context_data.
        """
        try:
            context.update({new_key: url_names.get(existing_key)})
        except InvalidUrlName as e:
            raise UrlRequestContextError(
                f"Url name not defined in url_names. "
                f"Expected one of {url_names.registry}. Got {e}. "
                f"Hint: check if dashboard middleware is loaded."
            )
        return context
