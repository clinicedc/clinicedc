from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urlencode
from uuid import UUID

from django.urls import reverse

from edc_dashboard.url_names import url_names

__all__ = ["NextQuerystring"]


@dataclass(kw_only=True)
class NextQuerystring:
    """Make a querystring that complies with the next_url concept
    used by edc_submit_line and modeladminmixin on save/cancel to
    redirect to the dashboard.

    `extra_kwargs` may be added to prepopulate form fields.

    A querystring might look like this:
    ?next=namespace:urlname,attr1,attr2&attr1=value1&attr2=value2

    See DashboardModelButton for example usage.
    """

    next_url_name: str = field(default="subject_dashboard_url")
    reverse_kwargs: dict[str, str | int | float | UUID] = field(default_factory=dict)
    extra_kwargs: dict[str, str | int | float | UUID] = field(default_factory=dict)
    label: str = field(default="next")
    next_url: str = field(default=None, init=False)
    querystring: str = field(default=None, init=False)

    def __post_init__(self):
        # check valid "next" url name
        next_url_name = url_names.get_or_raise(self.next_url_name)
        # check "next" url reverses
        self.next_url = reverse(next_url_name, kwargs=self.reverse_kwargs)
        # build querystring
        keys = ",".join(list(self.reverse_kwargs.keys()))
        qs_part1 = f"{self.label}={next_url_name}" + "," + keys
        self.reverse_kwargs.update(self.extra_kwargs)
        qs_part2 = urlencode(self.reverse_kwargs)
        self.querystring = qs_part1 + "&" + qs_part2
