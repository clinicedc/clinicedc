from django import template
from django.conf import settings
from django.urls.exceptions import NoReverseMatch
from django.urls.base import reverse


register = template.Library()


@register.inclusion_tag(
    f"edc_navbar/bootstrap{settings.EDC_BOOTSTRAP}/edc_navbar.html", takes_context=True
)
def edc_navbar(context):
    auth_user_change_url = None
    try:
        user = context.get("request").user
    except AttributeError:
        user = None
    else:
        try:
            auth_user_change_url = reverse("admin:auth_user_change", args=(user.id,))
        except NoReverseMatch:
            pass
    return dict(
        navbar=context.get("navbar"),
        default_navbar=context.get("default_navbar"),
        user=user,
        auth_user_change_url=auth_user_change_url,
    )
