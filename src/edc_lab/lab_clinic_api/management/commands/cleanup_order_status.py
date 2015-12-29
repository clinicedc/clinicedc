import logging
import re
from django.core.management.base import BaseCommand
from lis.exim.lab_import_dmis.classes import  DmisTools
from ...models import Order, Result

logger = logging.getLogger(__name__)


class NullHandler(logging.Handler):
    def emit(self, record):
        pass
nullhandler = logger.addHandler(NullHandler())


class Command(BaseCommand):

    args = ()
    help = 'Flag DUPLICATE, PENDING orders on EDC and django-lis as WITHDRAWN if they no longer exist on the DMIS.'

    def handle(self, *args, **options):
        # clear orphaned results
        # if a result exists with no result items it should not exist, so delete it
        dmis_tools = DmisTools()
        tot = Result.objects.filter(status='NEW').count()
        for n, result in enumerate(Result.objects.filter(status='NEW')):
            logger.info('{0} / {1} Result for order {2}'.format(n, tot, result.order.order_identifier))
            dmis_tools.clear_orphaned_result(result)
        #if an order is pending, confirm that the order id still exists on the DMIS
        # if not, delete it from both the django-lis and the EDC
        # note that order_identifer = lab21.id
        tot = Order.objects.filter(status='PENDING').count()
        invalid_identifiers = []
        for n, order in enumerate(Order.objects.filter(status='PENDING')):
            logger.info('{0} / {1} Order {2} {3}'.format(n, tot, order.order_identifier, order.aliquot.receive.receive_identifier))
            if not re.match('\d+', order.order_identifier):
                logger.warning('    invalid order identifier {0}'.format(order.order_identifier))
                invalid_identifiers.append(order.order_identifier)
            else:
                dmis_tools.flag_withdrawn_order(self, order, save=True)
        Order.objects.flag_duplicates()

