from django import template
from django.contrib.admin.templatetags.admin_modify import (
    submit_row as django_submit_row,
)

register = template.Library()


@register.inclusion_tag("edc_submit_line.html", takes_context=True)
def edc_submit_row(context):
    request = context.get("request")
    if request:
        if int(request.site.id) == int(context.get("reviewer_site_id", 0)):
            context.update({"save_next": None})
            context.update({"show_delete": None})
    try:
        show_save = context["show_save"]
    except KeyError:
        show_save = None
    try:
        context["save_next"]
    except KeyError:
        pass
    else:
        context["save_next"] = show_save
    return django_submit_row(context)


@register.inclusion_tag("edc_revision_line.html", takes_context=True)
def revision_row(context):
    return dict(
        copyright=context.get("copyright"),
        institution=context.get("institution"),
        revision=context.get("revision"),
        disclaimer=context.get("disclaimer"),
    )


@register.inclusion_tag("edc_instructions.html", takes_context=True)
def instructions(context):
    instructions = context.get("instructions")
    return {"instructions": instructions}


@register.inclusion_tag("edc_additional_instructions.html", takes_context=True)
def additional_instructions(context):
    additional_instructions = context.get("additional_instructions")
    notification_instructions = context.get("notification_instructions")
    return {
        "additional_instructions": additional_instructions,
        "notification_instructions": notification_instructions,
    }
