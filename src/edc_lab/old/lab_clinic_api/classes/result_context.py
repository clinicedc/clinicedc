from django.conf import settings

from ..models import Result, ResultItem


class ContextDescriptor(object):

    def __init__(self):
        self.value = {}

    def __get__(self, instance, owner):
        if instance.result_identifier:
            self.__set__(instance)
        return self.value

    def __set__(self, instance):
        self.value = {
            'last_updated': instance.result.modified,
            'result': instance.result,
            'protocol_identifier': settings.PROJECT_NUMBER,
            'subject_identifier': instance.registered_subject.subject_identifier,
            'dob': instance.registered_subject.dob,
            'is_dob_estimated': instance.registered_subject.is_dob_estimated,
            'gender': instance.registered_subject.gender,
            'visit': instance.result.order.aliquot.receive.visit,
            'initials': instance.registered_subject.initials,
            'site_identifier': instance.registered_subject.study_site.site_name,
            'clinicians_initials': instance.result.order.aliquot.receive.clinician_initials,
            'drawn_datetime': instance.result.order.aliquot.receive.drawn_datetime,
            'panel_name': instance.result.order.panel.edc_name,
            'receive_identifier': instance.result.order.aliquot.receive.receive_identifier,
            'receive_datetime': instance.result.order.aliquot.receive.receive_datetime,
            'aliquot_identifier': instance.result.order.aliquot.aliquot_identifier,
            'order_identifier': instance.result.order.order_identifier,
            'order_datetime': instance.result.order.order_datetime,
            'condition': instance.result.order.aliquot.receive.receive_condition,
            'result_items': instance.result_items,
            'action': "view",
            'section_name': instance.section_name,
            'search_name': instance.search_name,
            'result_include_file': "detail.html",
            'receiving_include_file': "receiving.html",
            'orders_include_file': "orders.html",
            'result_items_include_file': "result_items.html",
            'top_result_include_file': "result_include.html",
        }


class ResultContext(object):

    context = ContextDescriptor()

    def __init__(self, result_identifier, **kwargs):
        self.section_name = kwargs.get('section_name')
        self.search_name = kwargs.get('search_name')
        self.result_identifier = result_identifier
        if self.result_identifier:
            # get first one only, in coase of duplicates
            self.result = Result.objects.get(result_identifier=self.result_identifier)
            self.result_items = ResultItem.objects.filter(result=self.result)
            self.registered_subject = self.result.order.aliquot.receive.registered_subject
        else:
            self.result = None
            self.result_items = None
            self.registered_subject = None
