from warnings import warn

from django.db.models.constants import LOOKUP_SEP
from django.urls.base import reverse
from django.urls.exceptions import NoReverseMatch


class SearchTermLookupError(Exception):
    pass


def get_next_url(request, next_attr=None, warn_to_console=None):
    url = None
    next_url = None
    next_value = request.GET.dict().get(next_attr or "next")
    warn_to_console = True if warn_to_console is None else warn_to_console

    if next_value:
        kwargs = {}
        for pos, value in enumerate(next_value.split(",")):
            if pos == 0:
                next_url = value
            else:
                kwargs.update({value: request.GET.get(value)})
        try:
            url = reverse(next_url, kwargs=kwargs)
        except NoReverseMatch as e:
            if warn_to_console:
                warn(f"{e}. Got {next_value}.")
    return url


def get_value_from_lookup_string(search_field_name: str = None, obj=None, request=None):
    value = None
    for field in search_field_name.split(LOOKUP_SEP):
        if request:
            value = request.GET.get(field, "")
            break
        else:
            try:
                value = getattr(value or obj, field)
            except AttributeError as e:
                raise SearchTermLookupError(
                    f"Invalid search term. `{search_field_name}`. Got {e}"
                )
            if value is None:
                break
    return value
