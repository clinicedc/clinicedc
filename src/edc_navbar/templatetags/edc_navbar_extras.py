from __future__ import annotations

from django import template
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch

from ..navbar_item import NavbarItem

register = template.Library()


@register.inclusion_tag("edc_navbar/edc_navbar.html", takes_context=True)
def render_navbar(context) -> dict:
    auth_user_change_url = None
    user = getattr(context["request"], "user", None)
    user_id = getattr(user, "id", None)
    try:
        auth_user_change_url = reverse("edc_auth_admin:auth_user_change", args=(user_id,))
    except NoReverseMatch:
        pass
    return dict(
        auth_user_change_url=auth_user_change_url,
        default_navbar=context.get("default_navbar"),
        navbar=context.get("navbar"),
        user=user,
        request=context["request"],
    )


@register.inclusion_tag("edc_navbar/navbar_item.html", takes_context=True)
def render_navbar_item(context, navbar_item: NavbarItem) -> dict:
    data = {}
    url = navbar_item.get_url()
    navbar_item.set_disabled(user=getattr(context["request"], "user", None))
    if url:
        data.update(url=url)
    data.update(navbar_item=navbar_item)
    return data
