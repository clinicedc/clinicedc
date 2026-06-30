"""Shared site filter for the stock-take pages.

The stock-take home page and the discrepancy report share one ``?site=``
selection. "All sites" (no selection) leaves the bin list unfiltered.

Selector labels use the site *display name* from the ``edc_sites`` global
registry (``sites.get(site_id).description``), not the raw Site.name.
"""

from __future__ import annotations

from dataclasses import dataclass

from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet

from edc_sites.site import SiteNotRegistered, sites


@dataclass(frozen=True)
class SiteChoice:
    """A selectable site for the stock-take filter."""

    id: int
    display_name: str


def _display_name(site_id: int) -> str:
    """Display name from the edc_sites global, falling back to the id."""
    try:
        return sites.get(site_id).description
    except SiteNotRegistered:
        return str(site_id)


def stock_take_site_choices(bin_qs: QuerySet) -> list[SiteChoice]:
    """Sites that have at least one bin in ``bin_qs``, ordered by display name."""
    site_ids = (
        bin_qs.exclude(location__site__isnull=True)
        .values_list("location__site_id", flat=True)
        .distinct()
    )
    choices = [
        SiteChoice(id=site_id, display_name=_display_name(site_id)) for site_id in site_ids
    ]
    return sorted(choices, key=lambda choice: choice.display_name)


def get_selected_site_id(request: WSGIRequest, site_choices: list[SiteChoice]) -> int | None:
    """Return the chosen site id from ``?site=``, or None for "All sites".

    Anything that is not one of the offered sites is ignored.
    """
    raw = request.GET.get("site")
    if not raw:
        return None
    try:
        candidate = int(raw)
    except (TypeError, ValueError):
        return None
    valid_ids = {choice.id for choice in site_choices}
    return candidate if candidate in valid_ids else None
