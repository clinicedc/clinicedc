from django.shortcuts import render_to_response
from django.template.loader import render_to_string

from lis.specimen.lab_result_item.classes import ResultItemFlag
from lis.exim.lab_import_lis.classes import LisDataImporter
from lis.exim.lab_import_dmis.classes import Dmis

from ..models import Result, Order, ResultItem


class EdcLabResults(object):

    """ Accesses local lab data by subject."""

    def update(self, subject_identifier):
        """ Updates the local lab data with that from the Lis. """
        dmis = Dmis('lab_api')
        dmis.import_from_dmis(subject_identifier=subject_identifier)
        lis_data_importer = LisDataImporter('lab_api')
        last_updated = lis_data_importer.update_from_lis(subject_identifier=subject_identifier)
        return last_updated

    def render(self, subject_identifier, update=False):
        """ Renders local lab data for the subject's dashboard."""
        template = 'result_status_bar.html'
        last_updated = None
        if update:
            last_updated = self.update(subject_identifier)
        resulted = Result.objects.filter(
            order__aliquot__receive__registered_subject__subject_identifier=subject_identifier).order_by(
                '-order__aliquot__receive__drawn_datetime')
        if update:
            for result in resulted:
                for result_item in ResultItem.objects.filter(result=result):
                    if result_item.result_item_value_as_float:
                        result_item.reference_range, result_item.reference_flag, result_item.grade_range, result_item.grade_flag = ResultItemFlag().calculate(result_item)
                        result_item.save()
        ordered = (Order.objects.filter(aliquot__receive__registered_subject__subject_identifier=subject_identifier)
                                .exclude(order_identifier__in=[result.order.order_identifier for result in resulted])
                                .order_by('-aliquot__receive__drawn_datetime'))
        return render_to_string(template, {'resulted': resulted, 'ordered': ordered, 'last_updated': last_updated})

    def results_template(self, subject_identifier, update=False):
        """This method is a refactor of the above render method except that it renders to response"""
        template = "result_status_bar.html"
        return render_to_response(template, self.context_data(subject_identifier, update))

    def context_data(self, subject_identifier, update=False):
        resulted = self._query_resulted(subject_identifier)
        self._update_result_items(resulted)
        context = {'last_updated': self._last_updated(subject_identifier, update)}
        context['ordered'] = self._query_ordered(subject_identifier, resulted)
        context['resulted'] = self._query_resulted(subject_identifier)
        return context

    def _query_resulted(self, subject_identifier):
        criteria = {'order__aliquot__receive__registered_subject__subject_identifier': subject_identifier}
        return Result.objects.filter(**criteria).order_by('-order__aliquot__receive__drawn_datetime')

    def _query_ordered(self, subject_identifier, resulted):
        return (Order.objects.filter(aliquot__receive__registered_subject__subject_identifier=subject_identifier)
                .exclude(order_identifier__in=[result.order.order_identifier for result in resulted])
                .order_by('-aliquot__receive__drawn_datetime'))

    def _last_updated(self, subject_identifier, update=False):
        return self.update(subject_identifier) if update else None

    def _update_result_items(self, resulted):
        for result in resulted:
            for result_item in ResultItem.objects.filter(result=result):
                self._update_result_item(result_item)

    def _update_result_item(self, result_item):
        if result_item.result_item_value_as_float:
            result_item.reference_range, result_item.reference_flag, result_item.grade_range, result_item.grade_flag = ResultItemFlag().calculate(result_item)
            result_item.save()
