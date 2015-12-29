import logging
from django.core.management.base import BaseCommand
from lis.specimen.lab_test_code.models import TestCode as LisTestCode
from ...models import TestCode
from ...classes import ConvertLisAttr

logger = logging.getLogger(__name__)


class NullHandler(logging.Handler):
    def emit(self, record):
        pass
nullhandler = logger.addHandler(NullHandler())


class Command(BaseCommand):

    args = ()
    help = 'Imports test codes from the Lis.'

    def handle(self, *args, **options):
        convert_lis_attr = ConvertLisAttr()
        self.db = 'lab_api'
        count = LisTestCode.objects.using(self.db).all().count()
        for lis_test_code in LisTestCode.objects.using(self.db).all().order_by('code'):
            test_code, created = convert_lis_attr.test_code(lis_test_code)
            action = 'Adding'
            if not created:
                action = 'Updating'
            print '{action} {test_code}'.format(action=action, test_code=test_code)
        lis = [test_code.code for test_code in LisTestCode.objects.using(self.db).all().order_by('code')]
        local = [test_code.code for test_code in TestCode.objects.all().order_by('code')]
        diff_set = set(local).difference(set(lis))
        if diff_set:
            print 'Warning: found {0} in local but not lis.'.format(', '.join(diff_set))
        diff_set = set(lis).difference(set(local))
        if diff_set:
            print 'Warning: found {0} in lis but not local.'.format(', '.join(diff_set))
        print 'Done importing {new_count} / {count} test codes on Lis connection {db}.'.format(count=count,
                                                                                               new_count=TestCode.objects.all().count(),
                                                                                               db=self.db)
