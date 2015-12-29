import logging

from django.db import models

from lis.specimen.lab_result_item.models import BaseResultItem

from edc.lab.lab_clinic_reference.classes import ClinicReferenceFlag, ClinicGradeFlag
from edc_base.model.models import BaseUuidModel


from .test_code import TestCode
from .result import Result


logger = logging.getLogger(__name__)


class NullHandler(logging.Handler):
    def emit(self, record):
        pass
nullhandler = logger.addHandler(NullHandler())


class ResultItem(BaseResultItem, BaseUuidModel):
    """Stores each result item in a result in one-to-many relation with :class:`Result`."""
    test_code = models.ForeignKey(TestCode, related_name='+')
    result = models.ForeignKey(Result)
    subject_type = models.CharField(max_length=25, null=True)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        self.subject_identifier = self.result.order.aliquot.receive.registered_subject.subject_identifier
        self.receive_identifier = self.result.order.aliquot.receive.receive_identifier
        self.subject_type = self.get_subject_type()
        super(ResultItem, self).save(*args, **kwargs)

    def __unicode__(self):
        return unicode(self.test_code)

    def result_value(self):
        if self.result_item_value_as_float:
            return self.result_item_value_as_float
        else:
            return self.result_item_value

    def to_result(self):
        reviewed = ''
        result = '<a href="/admin/lab_clinic_api/result/?q={result_identifier}">result</a>'.format(result_identifier=self.result.result_identifier)
        if self.result.reviewed:
            reviewed = """&nbsp;<img src="/static/admin/img/icon_success.gif" width="10" height="10" alt="Reviewed"/>"""
        return '{result}{reviewed}'.format(result=result, reviewed=reviewed)
    to_result.allow_tags = True

    def get_report_datetime(self):
        return self.validation_datetime

    @property
    def get_drawn_datetime(self):
        return self.result.order.aliquot.receive.drawn_datetime

    def get_subject_type(self):
        if not self.subject_type:
            return self.result.order.aliquot.receive.registered_subject.subject_type
        else:
            return self.subject_type

    def get_grading_list(self):
        return ('grading_list', models.get_model('lab_clinic_reference', 'gradinglistitem'))

    def get_cls_reference_flag(self):
        return ClinicReferenceFlag

    def get_cls_grade_flag(self):
        return ClinicGradeFlag

    def get_reference_list(self):
        #pdb.set_trace()
        return ('reference_range_list', models.get_model('lab_clinic_reference', 'referencerangelistitem'))

    def get_test_code(self):
        return self.test_code.code

    def get_result_datetime(self):
        return self.result_item_datetime

    class Meta:
        app_label = "lab_clinic_api"
        ordering = ('-result_item_datetime', )
