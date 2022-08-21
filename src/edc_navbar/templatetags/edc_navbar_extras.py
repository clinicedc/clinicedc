from django import template
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from edc_dashboard.utils import get_bootstrap_version

register = template.Library()


@register.inclusion_tag(
    f"edc_navbar/bootstrap{get_bootstrap_version()}/edc_navbar.html", takes_context=True
)
def show_edc_navbar(context):
    auth_user_change_url = None
    try:
        user = context.get("request").user
    except AttributeError:
        user = None
    else:
        try:
            auth_user_change_url = reverse("edc_auth_admin:auth_user_change", args=(user.id,))
        except NoReverseMatch:
            pass
    return dict(
        auth_user_change_url=auth_user_change_url,
        default_navbar=context.get("default_navbar"),
        navbar=context.get("navbar"),
        user=user,
    )
