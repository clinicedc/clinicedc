from django import template

from ..site_prn_forms import site_prn_forms

register = template.Library()


@register.inclusion_tag('edc_prn/prn_list_items.html')
def prn_list_items(subject_identifier, **kwargs):
    prn_forms = []
    for prn in site_prn_forms:
        if prn.show_on_subject_dashboard(subject_identifier=subject_identifier):
            prn_forms.append(prn)
    return dict(prn_forms=prn_forms, subject_identifier=subject_identifier)
