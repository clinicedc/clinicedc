from django.core.exceptions import ObjectDoesNotExist


def print_pdf_report(
    self, model_cls=None, pdf_report_cls=None, action_identifier=None, request=None
):
    try:
        model_obj = model_cls.objects.get(action_identifier=action_identifier)
    except ObjectDoesNotExist:
        pass
    else:
        pdf_report = pdf_report_cls(
            death_report=model_obj,
            subject_identifier=model_obj.subject_identifier,
            user=self.request.user,
            request=request,
        )
        return pdf_report.render_to_response()
    return None
