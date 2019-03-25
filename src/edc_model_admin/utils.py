from django.urls.base import reverse
from django.urls.exceptions import NoReverseMatch


def get_next_url(request, next_attr=None):

    url = None
    kwargs = {}
    next_attr = next_attr or "next"

    options = request.GET.dict()
    next_value = options.get(next_attr)

    if next_value:
        try:
            next_url, parameter_string = next_value.split(",")
        except ValueError:
            next_url, parameter_string = next_value, ""

        if parameter_string:
            for param in parameter_string.split(","):
                kwargs.update({param: request.GET.get(param)})
        try:
            url = reverse(next_url, kwargs=kwargs)
        except NoReverseMatch:
            pass
    return url
