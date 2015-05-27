from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from ..classes import site_requisitions


@login_required
def view_requisition(request, **kwargs):
    requisition = None
    requisition_identifier_label = kwargs.get('requisition_identifier_label', 'specimen_identifier')
    identifier = kwargs.get('identifier', None)
    subject_type = kwargs.get('subject_type', None)
    template = 'requisition.html'
    if identifier and subject_type:
        requisition_cls = site_requisitions.get(subject_type)
        if requisition_cls:
            if requisition_cls.objects.filter(**{requisition_identifier_label: identifier}).exists():
                requisition = requisition_cls.objects.get(**{requisition_identifier_label: identifier})
    return render_to_response(template,
        {'requisition': requisition},
        context_instance=RequestContext(request)
        )
