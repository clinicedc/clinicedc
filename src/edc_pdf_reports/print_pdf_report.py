# from __future__ import annotations
#
# from typing import TYPE_CHECKING, Type
#
# from django.core.exceptions import ObjectDoesNotExist
#
# if TYPE_CHECKING:
#     from django.core.handlers.wsgi import WSGIRequest
#     from django.db import models
#
#     from edc_pdf_reports import CrfPdfReport
#
#     class Model(models.Model):
#         subject_identifier: str
#
#
# def print_pdf_report(
#     self,
#     model_cls: Model = None,
#     pdf_report_cls: Type[CrfPdfReport] = None,
#     action_identifier: str = None,
#     request: WSGIRequest = None,
# ):
#     try:
#         model_obj = model_cls.objects.get(action_identifier=action_identifier)
#     except ObjectDoesNotExist:
#         pass
#     else:
#         pdf_report = pdf_report_cls(
#             death_report=model_obj,
#             subject_identifier=model_obj.subject_identifier,
#             user=self.request.user,
#             request=request,
#         )
#         return pdf_report.render_to_response()
#     return None
