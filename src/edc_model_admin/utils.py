from django.urls.base import reverse
from django.urls.exceptions import NoReverseMatch
from warnings import warn


def get_next_url(request, next_attr=None):

    url = None
    next_value = request.GET.dict().get(next_attr or "next")
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
            warn(f"{e}. Got {next_value}.")
    return url
