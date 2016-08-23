from django.shortcuts import render_to_response

from ..classes import ResultContext, EdcLabResults


def view_lab_result(request, result_identifier):
    context = ResultContext(result_identifier).context
    return render_to_response('clinic_result_report_include.html', context)


def update_result_status(request, subject_identifier):
    return EdcLabResults().results_template(subject_identifier, update=True)
