from django.core.management.base import BaseCommand
from django.db.models import get_model
from lis.specimen.lab_result_item.classes import ResultItemFlag
from edc.subject.lab_tracker.classes import site_lab_tracker

site_lab_tracker.autodiscover()


class Command(BaseCommand):

    args = ()
    help = 'Recalculate grading and reference range flags for result items.'

    def handle(self, *args, **options):
        Result = get_model('lab_clinic_api', 'result')
        ResultItem = get_model('lab_clinic_api', 'resultitem')
        tot = Result.objects.all().count()
        for index, result in enumerate(Result.objects.all().order_by('result_identifier')):
            updated = 0
            print ('{0} / {1} Recalculating for {2}'.format(index, tot, result.result_identifier))
            for result_item in ResultItem.objects.filter(result=result):
                original_flags = (result_item.reference_range, result_item.reference_flag, result_item.grade_range, result_item.grade_flag)
                if result_item.result_item_value_as_float:
                    result_item.reference_range, result_item.reference_flag, result_item.grade_range, result_item.grade_flag = ResultItemFlag().calculate(result_item)
                    if original_flags != (result_item.reference_range, result_item.reference_flag, result_item.grade_range, result_item.grade_flag):
                        result_item.save()
                        updated += 1
                        print ('    UPDATED {0} to {1}'.format(result_item.test_code.code, result_item.grade_flag))
                    else:
                        print ('    no change {0} to {1}'.format(result_item.test_code.code, result_item.grade_flag))
        print ('Updated {0} of {1} reviewed. Check HistoryModelError model for errors.'.format(updated, index))
