from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

from ..classes import ResultContext


@login_required
def view_result(request, **kwargs):

    result_identifier = kwargs.get('result_identifier')
    result_context = ResultContext(result_identifier)
    return render_to_response(
        'clinic_result_report.html',
        result_context.context,
        context_instance=RequestContext(request)
        )
